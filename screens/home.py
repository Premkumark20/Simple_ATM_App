from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import database
from utils.styles import (
    ACCENT, CHIP_BG, CURRENCY, GREEN, MAX_AMOUNT, ORANGE, PRIMARY, RED,
    TEXT_ON_DARK_MUTED, WHITE, money,
)
from utils.widgets import Card, RoundedButton, StyledInput, Text, show_popup


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = ''
        root = BoxLayout(orientation='vertical')

        # ---- header with balance ----
        header = Card(orientation='vertical', bg_color=PRIMARY,
                      radius=[0, 0, dp(36), dp(36)], size_hint_y=None, height=dp(195),
                      padding=[dp(24), dp(16), dp(24), dp(18)], spacing=dp(1))
        header.add_widget(Widget())
        self.welcome_label = Text(text='Hello', font_size=sp(16), bold=True, color=WHITE, height=dp(24))
        header.add_widget(self.welcome_label)
        self.account_info = Text(text='Account No: RA2311018020002', font_size=sp(12),
                                 color=TEXT_ON_DARK_MUTED, height=dp(18))
        header.add_widget(self.account_info)
        header.add_widget(Text(text='Available balance', font_size=sp(12),
                               color=TEXT_ON_DARK_MUTED, height=dp(18)))
        self.balance_label = Text(text=money(0), font_size=sp(34), bold=True,
                                  color=WHITE, height=dp(48))
        header.add_widget(self.balance_label)
        root.add_widget(header)

        # ---- body ----
        body = BoxLayout(orientation='vertical', spacing=dp(10),
                         padding=[dp(20), dp(14), dp(20), dp(14)])

        chips = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        for value in (100, 500, 1000, 5000):
            chip = RoundedButton(text=f'{CURRENCY}{value:,}', bg_color=CHIP_BG, color=PRIMARY,
                                 height=dp(40), font_size=sp(14), radius=[dp(20)])
            chip.bind(on_release=lambda _btn, v=value: self.set_amount(v))
            chips.add_widget(chip)
        body.add_widget(chips)

        self.amount = StyledInput(hint_text='Enter amount', input_filter='float')
        body.add_widget(self.amount)

        self.reason = StyledInput(hint_text='Reason (e.g. Rent, Groceries, Gift)')
        body.add_widget(self.reason)

        actions = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        deposit_btn = RoundedButton(text='DEPOSIT', bg_color=GREEN)
        deposit_btn.bind(on_release=self.deposit)
        withdraw_btn = RoundedButton(text='WITHDRAW', bg_color=RED)
        withdraw_btn.bind(on_release=self.withdraw)
        actions.add_widget(deposit_btn)
        actions.add_widget(withdraw_btn)
        body.add_widget(actions)

        history_btn = RoundedButton(text='VIEW TRANSACTION HISTORY', bg_color=ACCENT)
        history_btn.bind(on_release=self.view_transactions)
        body.add_widget(history_btn)

        body.add_widget(Widget())

        logout_btn = RoundedButton(text='LOGOUT', bg_color=ORANGE)
        logout_btn.bind(on_release=self.ask_logout)
        body.add_widget(logout_btn)

        root.add_widget(body)
        # pyrefly: ignore [missing-attribute]
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.welcome_label.text = f'Account Name: {self.username}'
        self.amount.text = ''
        self.reason.text = ''
        self.update_balance()

    def update_balance(self):
        self.balance_label.text = money(database.get_balance(self.username))

    def set_amount(self, value):
        self.amount.text = str(value)

    def _read_amount(self):
        try:
            amount = round(float(self.amount.text), 2)
        except ValueError:
            show_popup('Invalid amount', 'Enter a valid amount.', 'error')
            return None
        if amount <= 0:
            show_popup('Invalid amount', 'Amount must be greater than zero.', 'error')
            return None
        if amount > MAX_AMOUNT:
            show_popup('Invalid amount', f'Maximum per transaction is {money(MAX_AMOUNT)}.', 'error')
            return None
        return amount

    def deposit(self, *args):
        amount = self._read_amount()
        if amount is None:
            return
        reason_text = self.reason.text.strip() or 'No Reason'
        new_balance = database.deposit(self.username, amount, reason=reason_text)
        self.amount.text = ''
        self.reason.text = ''
        self.update_balance()
        show_popup('Deposit successful',
                   f'{money(amount)} deposited ({reason_text}).\nNew balance: {money(new_balance)}', 'success')

    def withdraw(self, *args):
        amount = self._read_amount()
        if amount is None:
            return
        reason_text = self.reason.text.strip() or 'Withdrawal'
        try:
            new_balance = database.withdraw(self.username, amount, reason=reason_text)
        except database.InsufficientFunds as err:
            show_popup('Insufficient balance',
                       f'Your balance is {money(err.balance)}.\nYou cannot withdraw {money(amount)}.',
                       'error')
            return
        self.amount.text = ''
        self.reason.text = ''
        self.update_balance()
        show_popup('Withdrawal successful',
                   f'{money(amount)} withdrawn ({reason_text}).\nNew balance: {money(new_balance)}', 'success')

    def view_transactions(self, *args):
        self.manager.get_screen('transactions').load_transactions(self.username)
        self.manager.current = 'transactions'

    def ask_logout(self, *args):
        show_popup('Logout', 'Are you sure you want to log out?', 'info',
                   on_confirm=self.logout)

    def logout(self):
        self.username = ''
        self.manager.current = 'login'
