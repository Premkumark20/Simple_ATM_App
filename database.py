"""SQLite storage for the ATM app (hashed passwords, atomic transactions)."""
import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime

_db_path = 'atm.db'


class InsufficientFunds(Exception):
    def __init__(self, balance):
        super().__init__('Insufficient funds')
        self.balance = balance


def init(data_dir):
    """Set the database location and create the tables."""
    global _db_path
    os.makedirs(data_dir, exist_ok=True)
    _db_path = os.path.join(data_dir, 'atm.db')
    create_tables()
    ensure_admin()



def _connect():
    conn = sqlite3.connect(_db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def create_tables():
    with closing(_connect()) as conn, conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                balance_after REAL NOT NULL,
                date TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT 'No Reason',
                FOREIGN KEY (username) REFERENCES users (username)
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS del_transfer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                balance_after REAL NOT NULL,
                date TEXT NOT NULL,
                reason TEXT NOT NULL,
                deleted_at TEXT NOT NULL
            )''')

        # Auto-migrate reason column if missing in existing database
        cursor = conn.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'reason' not in columns:
            conn.execute("ALTER TABLE transactions ADD COLUMN reason TEXT NOT NULL DEFAULT 'No Reason'")


# ---------- password hashing ----------
def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return f'{salt.hex()}${digest.hex()}'


def _verify_password(password, stored):
    try:
        salt_hex, hash_hex = stored.split('$')
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    candidate = _hash_password(password, salt).split('$')[1]
    return hmac.compare_digest(candidate, hash_hex)


def _now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ---------- accounts ----------
def signup_user(username, password):
    """Create an account. Returns False if the username is taken."""
    try:
        with closing(_connect()) as conn, conn:
            conn.execute(
                'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
                (username, _hash_password(password), _now()))
        return True
    except sqlite3.IntegrityError:
        return False


def check_user(username, password):
    """Return the stored username if credentials are valid, else None."""
    with closing(_connect()) as conn:
        row = conn.execute(
            'SELECT username, password FROM users WHERE username = ?',
            (username,)).fetchone()
    if row and _verify_password(password, row[1]):
        return row[0]
    return None


def user_exists(username):
    """Check if a username exists in the system."""
    with closing(_connect()) as conn:
        row = conn.execute(
            'SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    return row is not None


def reset_password(username, new_password):
    """Reset user password. Returns True if successful, False if user does not exist."""
    with closing(_connect()) as conn, conn:
        user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            return False
        conn.execute(
            'UPDATE users SET password = ? WHERE username = ?',
            (_hash_password(new_password), username)
        )
        return True


def get_balance(username):
    with closing(_connect()) as conn:
        row = conn.execute(
            'SELECT balance FROM users WHERE username = ?', (username,)).fetchone()
    return row[0] if row else 0.0


# ---------- transactions ----------
def _apply(username, amount, kind, reason='No Reason'):
    with closing(_connect()) as conn, conn:      # commit / rollback automatically
        row = conn.execute(
            'SELECT balance FROM users WHERE username = ?', (username,)).fetchone()
        if row is None:
            raise ValueError('Unknown user')
        balance = row[0]
        new_balance = round(balance + amount if kind == 'Deposit' else balance - amount, 2)
        if new_balance < 0:
            raise InsufficientFunds(balance)
        conn.execute('UPDATE users SET balance = ? WHERE username = ?',
                     (new_balance, username))
        conn.execute(
            'INSERT INTO transactions (username, amount, transaction_type, balance_after, date, reason) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (username, amount, kind, new_balance, _now(), reason))
    return new_balance


def deposit(username, amount, reason='No Reason'):
    return _apply(username, amount, 'Deposit', reason or 'No Reason')


def withdraw(username, amount, reason='Withdrawal'):
    return _apply(username, amount, 'Withdraw', reason or 'Withdrawal')


def fetch_transactions(username, limit=200):
    """Rows: (id, date, reason, amount, type, balance_after), newest first."""
    with closing(_connect()) as conn:
        return conn.execute(
            'SELECT id, date, COALESCE(reason, "No Reason"), amount, transaction_type, balance_after '
            'FROM transactions WHERE username = ? ORDER BY id DESC LIMIT ?',
            (username, limit)).fetchall()


def backup_and_reset():
    """Re-index transaction IDs sequentially."""
    with closing(_connect()) as conn, conn:
        conn.execute('''
            CREATE TEMP TABLE temp_txns AS
            SELECT username, amount, transaction_type, balance_after, date, COALESCE(reason, "No Reason") as reason
            FROM transactions ORDER BY id ASC
        ''')
        conn.execute('DELETE FROM transactions')
        conn.execute('''
            INSERT INTO transactions (username, amount, transaction_type, balance_after, date, reason)
            SELECT username, amount, transaction_type, balance_after, date, reason FROM temp_txns
        ''')
        conn.execute('DROP TABLE temp_txns')


def delete_latest_transaction(username, transaction_id=None):
    """Delete the latest (most recent) transaction for a user, copy to del_transfer backup, and adjust user balance."""
    with closing(_connect()) as conn, conn:
        if transaction_id:
            latest = conn.execute(
                'SELECT id, date, COALESCE(reason, "No Reason"), amount, transaction_type FROM transactions '
                'WHERE username = ? ORDER BY id DESC LIMIT 1',
                (username,)).fetchone()
            if not latest or latest[0] != transaction_id:
                raise ValueError('Only the most recent transaction can be deleted.')
        else:
            latest = conn.execute(
                'SELECT id, date, COALESCE(reason, "No Reason"), amount, transaction_type FROM transactions '
                'WHERE username = ? ORDER BY id DESC LIMIT 1',
                (username,)).fetchone()
            if not latest:
                raise ValueError('No transactions to delete.')

        t_id, date, reason, amount, kind = latest

        row = conn.execute(
            'SELECT balance FROM users WHERE username = ?', (username,)).fetchone()
        if not row:
            raise ValueError('Unknown user')
        current_balance = row[0]

        if kind.lower() == 'deposit':
            new_balance = round(current_balance - amount, 2)
        elif kind.lower() == 'withdraw':
            new_balance = round(current_balance + amount, 2)
        else:
            new_balance = current_balance

        if new_balance < 0:
            raise InsufficientFunds(current_balance)

        # Copy to del_transfer backup table
        conn.execute(
            'INSERT INTO del_transfer (username, amount, transaction_type, balance_after, date, reason, deleted_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (username, amount, kind, new_balance, date, reason, _now()))

        conn.execute('DELETE FROM transactions WHERE id = ?', (t_id,))
        conn.execute('UPDATE users SET balance = ? WHERE username = ?',
                     (new_balance, username))

    return new_balance


def delete_all_transactions(username):
    """Move all user transactions to del_transfer and reset user balance to 0."""
    with closing(_connect()) as conn, conn:
        rows = conn.execute(
            'SELECT id, date, COALESCE(reason, "No Reason"), amount, transaction_type, balance_after '
            'FROM transactions WHERE username = ?', (username,)).fetchall()
        if not rows:
            return 0
        for t_id, date, reason, amount, kind, bal in rows:
            conn.execute(
                'INSERT INTO del_transfer (username, amount, transaction_type, balance_after, date, reason, deleted_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, amount, kind, bal, date, reason, _now()))
        conn.execute('DELETE FROM transactions WHERE username = ?', (username,))
        conn.execute('UPDATE users SET balance = 0.0 WHERE username = ?', (username,))
        return len(rows)


# ---------- admin functions ----------
def ensure_admin():
    """Ensure the default admin account exists with credentials admin / admin123."""
    with closing(_connect()) as conn, conn:
        row = conn.execute('SELECT id, password FROM users WHERE username = ?', ('admin',)).fetchone()
        if not row:
            conn.execute(
                'INSERT INTO users (username, password, balance, created_at) VALUES (?, ?, ?, ?)',
                ('admin', _hash_password('admin123'), 0.0, _now())
            )
        elif not _verify_password('admin123', row[1]):
            conn.execute(
                'UPDATE users SET password = ? WHERE username = ?',
                (_hash_password('admin123'), 'admin')
            )


def fetch_all_users():
    """Fetch all users (excluding admin) with their balance and transaction counts."""
    with closing(_connect()) as conn:
        return conn.execute('''
            SELECT u.id, u.username, u.balance, u.created_at, COUNT(t.id) as txn_count
            FROM users u
            LEFT JOIN transactions t ON u.username = t.username
            WHERE u.username != 'admin'
            GROUP BY u.id
            ORDER BY u.id DESC
        ''').fetchall()


def delete_user(username):
    """Delete a user and all their transactions. Prevents deleting the admin account."""
    if username.lower() == 'admin':
        raise ValueError('Cannot delete the admin account.')
    with closing(_connect()) as conn, conn:
        # Copy user transactions to del_transfer first
        rows = conn.execute(
            'SELECT id, date, COALESCE(reason, "No Reason"), amount, transaction_type, balance_after '
            'FROM transactions WHERE username = ?', (username,)).fetchall()
        for t_id, date, reason, amount, kind, bal in rows:
            conn.execute(
                'INSERT INTO del_transfer (username, amount, transaction_type, balance_after, date, reason, deleted_at) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (username, amount, kind, bal, date, reason, _now()))

        conn.execute('DELETE FROM transactions WHERE username = ?', (username,))
        conn.execute('DELETE FROM users WHERE username = ?', (username,))
    return True


def get_system_stats():
    """Get system stats for the admin portal: total users, total deposits, total transactions."""
    with closing(_connect()) as conn:
        total_users = conn.execute(
            "SELECT COUNT(*) FROM users WHERE username != 'admin'").fetchone()[0]
        total_balance = conn.execute(
            "SELECT COALESCE(SUM(balance), 0.0) FROM users WHERE username != 'admin'").fetchone()[0]
        total_txns = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE username != 'admin'").fetchone()[0]
    return {
        'total_users': total_users,
        'total_balance': total_balance,
        'total_transactions': total_txns
    }

