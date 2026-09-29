from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import database
from utils.styles import GRAY_BTN, GREEN, PRIMARY, TEXT_MUTED
from utils.widgets import Header, RoundedButton, StyledInput, Text, show_popup


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical')
        root.add_widget(Header('CREATE ACCOUNT', 'Join in less than a minute',
                               badge=False, height=dp(150)))

        body = BoxLayout(orientation='vertical', spacing=dp(14),
                         padding=[dp(24), dp(22), dp(24), dp(16)])
        body.add_widget(Text(text='Your details', font_size=sp(20), bold=True,
                             color=PRIMARY, height=dp(30)))
        body.add_widget(Text(text='Username: 3+ characters. Password: 4+ characters.',
                             font_size=sp(13), color=TEXT_MUTED, height=dp(20)))

        self.new_username = StyledInput(hint_text='Username')
        self.new_password = StyledInput(hint_text='Password', password=True)
        self.confirm_password = StyledInput(hint_text='Confirm password', password=True)
        self.new_username.bind(on_text_validate=lambda *_: setattr(self.new_password, 'focus', True))
        self.new_password.bind(on_text_validate=lambda *_: setattr(self.confirm_password, 'focus', True))
        self.confirm_password.bind(on_text_validate=lambda *_: self.create_account())
        body.add_widget(self.new_username)
        body.add_widget(self.new_password)
        body.add_widget(self.confirm_password)

        create_btn = RoundedButton(text='CREATE ACCOUNT', bg_color=GREEN)
        create_btn.bind(on_release=self.create_account)
        body.add_widget(create_btn)

        back_btn = RoundedButton(text='BACK TO LOGIN', bg_color=GRAY_BTN)
        back_btn.bind(on_release=self.go_to_login)
        body.add_widget(back_btn)

        body.add_widget(Widget())
        root.add_widget(body)
        # pyrefly: ignore [missing-attribute]
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.new_username.text = ''
        self.new_password.text = ''
        self.confirm_password.text = ''

    def create_account(self, *args):
        user = self.new_username.text.strip()
        pwd = self.new_password.text
        confirm = self.confirm_password.text

        if len(user) < 3:
            show_popup('Signup failed', 'Username must be at least 3 characters.', 'error')
            return
        if len(pwd) < 4:
            show_popup('Signup failed', 'Password must be at least 4 characters.', 'error')
            return
        if pwd != confirm:
            self.confirm_password.text = ''
            show_popup('Signup failed', 'Passwords do not match.', 'error')
            return

        if database.signup_user(user, pwd):
            show_popup('Account created', 'You can now log in.', 'success',
                       on_close=self.go_to_login)
        else:
            show_popup('Signup failed', 'That username is already taken.\nTry another.', 'error')

    def go_to_login(self, *args):
        self.manager.current = 'login'