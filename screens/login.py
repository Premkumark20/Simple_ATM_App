from utils.styles import GRAY_BTN
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

import database
from utils.styles import ORANGE, PRIMARY, PRIMARY_LIGHT, TEXT_MUTED
from utils.widgets import Header, RoundedButton, StyledInput, Text, show_popup


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attempts = 0
        root = BoxLayout(orientation='vertical')
        root.add_widget(Header('ATM BANKING', 'Secure and fast banking', height=dp(200)))

        body = BoxLayout(orientation='vertical', spacing=dp(10),
                         padding=[dp(24), dp(16), dp(24), dp(12)])
        body.add_widget(Text(text='Welcome back', font_size=sp(22), bold=True,
                             color=PRIMARY, height=dp(30)))
        body.add_widget(Text(text='Sign in to continue', font_size=sp(14),
                             color=TEXT_MUTED, height=dp(20)))

        self.username = StyledInput(hint_text='Username')
        self.password = StyledInput(hint_text='Password', password=True)
        self.username.bind(on_text_validate=lambda *_: setattr(self.password, 'focus', True))
        self.password.bind(on_text_validate=lambda *_: self.login())
        body.add_widget(self.username)
        body.add_widget(self.password)

        login_btn = RoundedButton(text='LOGIN', bg_color=PRIMARY)
        login_btn.bind(on_release=self.login)
        body.add_widget(login_btn)

        signup_btn = RoundedButton(text='CREATE NEW ACCOUNT', bg_color=ORANGE)
        signup_btn.bind(on_release=self.go_to_signup)
        body.add_widget(signup_btn)

        row_extra = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        forgot_btn = RoundedButton(text='FORGOT PASSWORD?', bg_color=TEXT_MUTED, font_size=sp(11))
        forgot_btn.bind(on_release=lambda *_: self.prompt_reset_password(self.username.text.strip()))
        admin_btn = RoundedButton(text='ADMIN PORTAL', bg_color=PRIMARY_LIGHT, font_size=sp(11))
        admin_btn.bind(on_release=self.quick_admin_login)
        row_extra.add_widget(forgot_btn)
        row_extra.add_widget(admin_btn)
        body.add_widget(row_extra)

        body.add_widget(Widget())
        root.add_widget(body)
        # pyrefly: ignore [missing-attribute]
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.username.text = ''
        self.password.text = ''
        self.attempts = 0

    def quick_admin_login(self, *args):
        self.username.text = 'admin'
        self.password.text = 'admin123'
        self.login()

    def login(self, *args):
        user = self.username.text.strip()
        pwd = self.password.text
        if not user or not pwd:
            show_popup('Login error', 'Enter both username and password.', 'error')
            return

        name = database.check_user(user, pwd)
        if name:
            self.attempts = 0
            if name.lower() == 'admin':
                self.manager.current = 'admin'
            else:
                home = self.manager.get_screen('home')
                home.username = name
                self.manager.current = 'home'
        else:
            self.attempts += 1
            self.password.text = ''
            if self.attempts >= 3:
                show_popup('Login Lockout',
                           'Too many failed login attempts.\nWould you like to reset your password?',
                           'error',
                           on_confirm=lambda: self.prompt_reset_password(user))
            else:
                show_popup('Login failed',
                           f'Invalid username or password.\nRemaining attempts: {3 - self.attempts}',
                           'error')

    def prompt_reset_password(self, initial_user=''):
        from kivy.uix.popup import Popup
        from utils.styles import WHITE

        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        content.add_widget(Text(text='Enter username and new password:', font_size=sp(14),
                                color=PRIMARY, height=dp(24)))

        user_input = StyledInput(hint_text='Username', text=initial_user)
        new_pwd = StyledInput(hint_text='New Password', password=True)
        conf_pwd = StyledInput(hint_text='Confirm Password', password=True)

        content.add_widget(user_input)
        content.add_widget(new_pwd)
        content.add_widget(conf_pwd)

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel_btn = RoundedButton(text='CANCEL', bg_color=GRAY_BTN, height=dp(44), font_size=sp(13))
        submit_btn = RoundedButton(text='RESET PASSWORD', bg_color=PRIMARY, height=dp(44), font_size=sp(13))

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(submit_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Password Reset', content=content,
                      size_hint=(0.9, None), size_hint_max_x=dp(420), height=dp(340),
                      background='', background_color=WHITE,
                      title_color=PRIMARY, title_size=sp(18), title_align='center',
                      separator_color=PRIMARY)

        cancel_btn.bind(on_release=lambda *_: popup.dismiss())

        def do_reset(*_):
            u = user_input.text.strip()
            p1 = new_pwd.text
            p2 = conf_pwd.text
            if not u or not p1 or not p2:
                show_popup('Error', 'Please fill in all fields.', 'error')
                return
            if p1 != p2:
                show_popup('Error', 'Passwords do not match.', 'error')
                return
            if not database.user_exists(u):
                show_popup('Error', f"User '{u}' does not exist.", 'error')
                return

            if database.reset_password(u, p1):
                popup.dismiss()
                self.attempts = 0
                show_popup('Success', 'Password reset successfully! You can now log in.', 'success')
            else:
                show_popup('Error', 'Password reset failed.', 'error')

        submit_btn.bind(on_release=do_reset)
        popup.open()

    def go_to_signup(self, *args):
        self.manager.current = 'signup'

