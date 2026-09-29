from datetime import datetime

from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import database
from utils.styles import (
    GREEN, PRIMARY, PRIMARY_LIGHT, RED, TEXT_MUTED, TEXT_ON_DARK_MUTED, WHITE, money
)
from utils.widgets import Card, RoundedButton, Text, show_popup


def _format_date(raw):
    try:
        return datetime.strptime(raw, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y %H:%M:%S')
    except (ValueError, TypeError):
        return str(raw)


class TransactionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_username = ''
        root = BoxLayout(orientation='vertical')

        header = Card(orientation='vertical', bg_color=PRIMARY,
                      radius=[0, 0, dp(36), dp(36)], size_hint_y=None, height=dp(110),
                      padding=[dp(20), dp(16), dp(20), dp(18)], spacing=dp(2))
        header.add_widget(Text(text='TRANSACTION HISTORY', font_size=sp(22), bold=True,
                               color=WHITE, halign='center', height=dp(34)))
        self.subtitle = Text(text='', font_size=sp(14), color=TEXT_ON_DARK_MUTED,
                             halign='center', height=dp(22))
        header.add_widget(self.subtitle)
        root.add_widget(header)

        # Action command bar (Remove One / Remove All)
        action_bar = BoxLayout(size_hint_y=None, height=dp(42), padding=[dp(16), dp(4)], spacing=dp(10))
        rem_one_btn = RoundedButton(text='REMOVE ONE', bg_color=RED, font_size=sp(11), height=dp(34))
        rem_one_btn.bind(on_release=self.remove_one)

        rem_all_btn = RoundedButton(text='REMOVE ALL', bg_color=RED, font_size=sp(11), height=dp(34))
        rem_all_btn.bind(on_release=self.remove_all)

        action_bar.add_widget(rem_one_btn)
        action_bar.add_widget(rem_all_btn)
        root.add_widget(action_bar)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.list = GridLayout(cols=1, spacing=dp(8), size_hint_y=None,
                               padding=[dp(16), dp(8), dp(16), dp(12)])
        # pyrefly: ignore [missing-attribute]
        self.list.bind(minimum_height=self.list.setter('height'))
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        footer = BoxLayout(size_hint_y=None, height=dp(70), padding=[dp(20), dp(10)])
        back_btn = RoundedButton(text='BACK TO HOME', bg_color=PRIMARY)
        back_btn.bind(on_release=self.go_back)
        footer.add_widget(back_btn)
        root.add_widget(footer)

        # pyrefly: ignore [missing-attribute]
        self.add_widget(root)

    def load_transactions(self, username):
        self.current_username = username
        self.list.clear_widgets()
        rows = database.fetch_transactions(username)
        self.subtitle.text = f'{username}  |  {len(rows)} transactions'

        if not rows:
            self.list.add_widget(Text(text='No transactions yet', font_size=sp(18), bold=True,
                                      color=PRIMARY, halign='center', height=dp(60)))
            self.list.add_widget(Text(text='Make a deposit or withdrawal to see entries.', color=TEXT_MUTED,
                                      halign='center', height=dp(30)))
            return

        for idx, (_id, date, reason, amount, kind, balance) in enumerate(rows):
            self.list.add_widget(self._make_row(_id, date, reason, amount, kind, balance))

    def _make_row(self, transaction_id, date, reason, amount, kind, balance):
        is_deposit = kind.lower() == 'deposit'
        color = GREEN if is_deposit else RED
        sign = '+' if is_deposit else '-'

        row = Card(orientation='horizontal', size_hint_y=None, height=dp(70),
                   padding=[dp(16), dp(8)], spacing=dp(8), radius=[dp(14)])

        left = BoxLayout(orientation='vertical')
        left.add_widget(Text(text=f"{kind}  [{reason}]", bold=True, font_size=sp(14),
                             size_hint_y=0.55, color=PRIMARY))
        left.add_widget(Text(text=_format_date(date), font_size=sp(11),
                             color=TEXT_MUTED, size_hint_y=0.45))
        row.add_widget(left)

        right = BoxLayout(orientation='vertical')
        right.add_widget(Text(text=f'{sign}{money(amount)}', bold=True, color=color,
                              halign='right', size_hint_y=0.55))
        right.add_widget(Text(text=f'Bal: {money(balance)}', font_size=sp(11),
                              color=TEXT_MUTED, halign='right', size_hint_y=0.45))
        row.add_widget(right)

        return row

    def do_delete(self, transaction_id=None):
        try:
            new_balance = database.delete_latest_transaction(self.current_username, transaction_id)
            if self.manager and self.manager.has_screen('home'):
                self.manager.get_screen('home').update_balance()
            self.load_transactions(self.current_username)
            show_popup('Transaction Removed', f'Latest row removed.\nNew balance: {money(new_balance)}', 'success')
        except Exception as e:
            show_popup('Delete Failed', str(e), 'error')

    def remove_one(self, *args):
        if not self.current_username:
            return
        show_popup('Remove Last Row',
                   'Remove and backup the most recent transaction row?',
                   'info',
                   on_confirm=lambda: self.do_delete(None))

    def remove_all(self, *args):
        if not self.current_username:
            return
        show_popup('Remove All Rows',
                   'Remove all transactions for this account and move them to backup?\nAccount balance will be reset to $0.',
                   'error',
                   on_confirm=self.do_remove_all)

    def do_remove_all(self):
        try:
            count = database.delete_all_transactions(self.current_username)
            if self.manager and self.manager.has_screen('home'):
                self.manager.get_screen('home').update_balance()
            self.load_transactions(self.current_username)
            show_popup('Removed All', f'{count} transaction rows moved to backup.', 'success')
        except Exception as e:
            show_popup('Error', str(e), 'error')

    def go_back(self, *args):
        self.manager.current = 'home'


