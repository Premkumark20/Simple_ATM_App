# ATM Banking Application (Desktop & Android)  

⬇️ [APK DOWNLOAD (Android)](https://github.com/Premkumark20/Simple_ATM_App/actions/runs/36595636566/artifacts/11045994249) &nbsp;|&nbsp; ⬇️ [WINDOWS DOWNLOAD (.exe)](https://github.com/Premkumark20/Simple_ATM_App/releases/latest/download/ATMBanking.zip)
  
A modern, cross-platform ATM Banking mobile and desktop application built with Python and Kivy GUI, powered by an embedded SQLite database (`atm.db`). No external database servers (like MySQL) are required—the application runs 100% self-contained on both **Windows Desktop** and **Android Devices**.  
  
---  
  
## 🛠️ Working Conditions & Prerequisites  
  
### 1. Supported Operating Systems & Platforms  
- **Windows Desktop**: Windows 10 / 11 (Standalone `.exe` or via Python environment)  
- **Android Mobile**: Android 5.0 (Lollipop) or higher (`.apk`)  
  
### 2. Runtime & Dependencies (For Python Development)  
- **Python**: 3.10+  
- **GUI Framework**: Kivy 2.3.1  
- **Database Engine**: Embedded SQLite (`sqlite3`) — **No external database server required**  
- **Zero Configuration**: Database tables (`users`, `transactions`, `del_transfer`) and default admin credentials are automatically initialized.  
  
Install required dependencies:  
```bash  
pip install kivy  
```  
  
---  
  
## ✨ Features & Functionalities  
  
### 👤 1. User Authentication & Security  
- **Account Registration & Login**: User sign-up with unique username validation and password confirmation matching.  
- **Password Security**: Passwords stored using PBKDF2-HMAC-SHA256 hashing with unique per-user salts.  
- **3-Attempt Login Protection**: Tracks failed login attempts with lockout alert.  
- **Password Reset**: "Forgot Password?" recovery workflow allows resetting account password.  
  
### 💳 2. ATM Banking Operations  
- **Account Info & Live Balance**: Displays Account Name, Account Number, and real-time available balance.  
- **Deposit Cash**: Quick deposit chip buttons ($100, $500, $1,000, $5,000) or custom deposit entry with optional reason (default *No Reason*).  
- **Withdraw Cash**: Cash withdrawal with immediate insufficient funds validation and balance protection with custom reason logging (default *Withdrawal*).  
  
### 📜 3. Transaction History & Management  
- **Transaction Log Cards**: Displays transaction type (Deposit/Withdraw), date/timestamp (`DD-MM-YYYY HH:MM:SS`), reason (`[Rent]`, `[Groceries]`), transaction amount, and post-transaction balance.  
- **`REMOVE ONE`**: Removes the most recent transaction and backs it up into the `del_transfer` table while adjusting balance.  
- **`REMOVE ALL`**: Backs up all user transaction history to `del_transfer` and resets account balance to `$0.00`.  
  
### 🛡️ 4. Admin Management Portal  
- **Default Admin Credentials**:  
  - **Username**: `admin`  
  - **Password**: `admin123`  
- **System Metrics Dashboard**:  
  - Total Registered Users  
  - Total System Funds ($)  
  - Total Processed Transactions  
- **User Account Management**: View list of registered accounts with balance and transaction count. Delete user accounts with complete transaction history cleanup.  
  
### 📱 5. Mobile & Desktop Navigation Features  
- **Hardware Integration**: Supports Android native back button and Desktop `Esc` key for screen navigation.  
- **Responsive Layout**: Optimized 420x760 mobile aspect ratio on Desktop and adaptive full-screen layout on Android.  
  
---  
  
## 🎮 Application Navigation  
  
| Screen | Functionality |  
| :--- | :--- |  
| **Login Screen** | Sign in with username & password, quick Admin login, or trigger Password Reset |  
| **Signup Screen** | Register new account with password confirmation |  
| **Home Screen** | View account info, balance, execute deposits/withdrawals with reasons, or open History |  
| **Transactions Screen** | View formatted transaction log with `REMOVE ONE` and `REMOVE ALL` buttons |  
| **Admin Portal** | System statistics dashboard and user account management with user deletion |  
  
---  
  
## 🚀 How to Run & Deploy  
  
### Option 1: Run via Python (Desktop)  
```bash  
python main.py  
```  
  
### Option 2: Windows Standalone Executable  
Double-click `ATMBanking.exe` on your desktop (single-file distribution compiled via `ATMBanking.spec`, no Python installation needed).  
  
### Option 3: Build & Install Android APK  
- **Automated GitHub Actions**: Push code to your GitHub repository to trigger `.github/workflows/buildozer.yml` and download the compiled `.apk` artifact.  
- **Local / Colab Build**: Compile using Buildozer (`buildozer.spec`):  
  ```bash  
  buildozer android debug  
  ```  
  Install the generated `.apk` from `bin/` onto your Android device. 
