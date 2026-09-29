"""Admin Portal - Display all registered users and manage user deletion."""
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import database
from utils.styles import (
    ACCENT, CHIP_BG, GREEN, PRIMARY, PRIMARY_LIGHT, RED, ORANGE,
    TEXT_MUTED, TEXT_ON_DARK_MUTED, WHITE, money
)
from utils.widgets import Card, RoundedButton, Text, show_popup


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')

        # ---- Top Header ----
        header = Card(orientation='vertical', bg_color=PRIMARY,
                      radius=[0, 0, dp(32), dp(32)], size_hint_y=None, height=dp(110),
                      padding=[dp(20), dp(14), dp(20), dp(16)], spacing=dp(2))
        header.add_widget(Text(text='ADMIN PORTAL', font_size=sp(22), bold=True,
                               color=WHITE, halign='center', height=dp(34)))
        self.header_sub = Text(text='System Management & User Database', font_size=sp(13),
                               color=TEXT_ON_DARK_MUTED, halign='center', height=dp(20))
        header.add_widget(self.header_sub)
        root.add_widget(header)

        # ---- Stats Bar ----
        stats_container = BoxLayout(size_hint_y=None, height=dp(76),
                                    padding=[dp(16), dp(8), dp(16), dp(4)])
        stats_box = Card(orientation='horizontal', bg_color=CHIP_BG,
                         padding=[dp(12), dp(6)], spacing=dp(8), radius=[dp(14)])

        self.users_stat = Text(text='Users: 0', font_size=sp(13), bold=True,
                               color=PRIMARY, halign='center')
        self.funds_stat = Text(text='Funds: $0', font_size=sp(13), bold=True,
                               color=GREEN, halign='center')
        self.txns_stat = Text(text='Txns: 0', font_size=sp(13), bold=True,
                              color=PRIMARY_LIGHT, halign='center')

        stats_box.add_widget(self.users_stat)
        stats_box.add_widget(self.funds_stat)
        stats_box.add_widget(self.txns_stat)
        stats_container.add_widget(stats_box)
        root.add_widget(stats_container)


        # ---- User list header ----
        sub_bar = BoxLayout(size_hint_y=None, height=dp(34),
                            padding=[dp(20), 0, dp(20), 0], spacing=dp(8))
        sub_bar.add_widget(Text(text='REGISTERED USERS', bold=True, font_size=sp(14),
                                color=PRIMARY, size_hint_x=0.7))
        refresh_btn = RoundedButton(text='REFRESH', bg_color=ACCENT, font_size=sp(11),
                                    size_hint_x=0.3, height=dp(30))
        refresh_btn.bind(on_release=lambda *_: self.load_data())
        sub_bar.add_widget(refresh_btn)
        root.add_widget(sub_bar)

        # ---- Scrollable Users List ----
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.list = GridLayout(cols=1, spacing=dp(10), size_hint_y=None,
                               padding=[dp(16), dp(8), dp(16), dp(8)])
        # pyrefly: ignore [missing-attribute]
        self.list.bind(minimum_height=self.list.setter('height'))
        scroll.add_widget(self.list)
        root.add_widget(scroll)

        # ---- Footer ----
        footer = BoxLayout(size_hint_y=None, height=dp(72), padding=[dp(20), dp(10)])
        logout_btn = RoundedButton(text='EXIT ADMIN (LOGOUT)', bg_color=ORANGE)
        logout_btn.bind(on_release=self.ask_logout)
        footer.add_widget(logout_btn)
        root.add_widget(footer)

        # pyrefly: ignore [missing-attribute]
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.load_data()

    def load_data(self):
        # Update stats
        stats = database.get_system_stats()
        self.users_stat.text = f"Users: {stats['total_users']}"
        self.funds_stat.text = f"Funds: {money(stats['total_balance'])}"
        self.txns_stat.text = f"Txns: {stats['total_transactions']}"

        # Populate user cards
        self.list.clear_widgets()
        users = database.fetch_all_users()

        if not users:
            self.list.add_widget(Text(text='No registered users found.', font_size=sp(16),
                                      bold=True, color=PRIMARY, halign='center', height=dp(60)))
            self.list.add_widget(Text(text='Accounts created through signup will appear here.',
                                      color=TEXT_MUTED, halign='center', height=dp(30)))
            return

        for user_id, username, balance, created_at, txn_count in users:
            self.list.add_widget(self._make_user_card(username, balance, created_at, txn_count))

    def _make_user_card(self, username, balance, created_at, txn_count):
        card = Card(orientation='horizontal', size_hint_y=None, height=dp(74),
                    padding=[dp(14), dp(8)], spacing=dp(10), radius=[dp(14)])

        # Left Column: Username & Joined Date
        left = BoxLayout(orientation='vertical', size_hint_x=0.45)
        left.add_widget(Text(text=username, bold=True, font_size=sp(16),
                             color=PRIMARY, size_hint_y=0.55))
        left.add_widget(Text(text=f"Joined: {created_at[:10]}", font_size=sp(11),
                             color=TEXT_MUTED, size_hint_y=0.45))
        card.add_widget(left)

        # Middle Column: Balance & Txn count
        mid = BoxLayout(orientation='vertical', size_hint_x=0.35)
        mid.add_widget(Text(text=money(balance), bold=True, font_size=sp(15),
                            color=GREEN, halign='right', size_hint_y=0.55))
        mid.add_widget(Text(text=f"{txn_count} transactions", font_size=sp(11),
                            color=TEXT_MUTED, halign='right', size_hint_y=0.45))
        card.add_widget(mid)

        # Right Column: Delete User Button
        del_btn = RoundedButton(text='DELETE', bg_color=RED, font_size=sp(11),
                                size_hint_x=None, width=dp(70), height=dp(38))
        del_btn.bind(on_release=lambda *_, u=username: self.confirm_delete_user(u))
        card.add_widget(del_btn)

        return card

    def confirm_delete_user(self, username):
        show_popup(
            'Delete User Account',
            f"Are you sure you want to delete user '{username}'?\n"
            f"All account balance and transaction records will be permanently erased.",
            'info',
            on_confirm=lambda: self.do_delete_user(username)
        )

    def do_delete_user(self, username):
        try:
            database.delete_user(username)
            self.load_data()
            show_popup('User Deleted', f"User '{username}' was permanently removed.", 'success')
        except Exception as e:
            show_popup('Error', str(e), 'error')

    def ask_logout(self, *args):
        show_popup('Logout', 'Log out of Admin Portal?', 'info', on_confirm=self.logout)

    def logout(self):
        self.manager.current = 'login'
