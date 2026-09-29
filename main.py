"""ATM Banking - application entry point."""
import os
import sys

# Prevent Kivy from parsing CLI arguments
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.config import Config
from kivy.utils import platform

# Window settings must be applied BEFORE importing kivy.core.window
if platform not in ('android', 'ios'):
    Config.set('graphics', 'width', '420')
    Config.set('graphics', 'height', '760')
    Config.set('input', 'mouse', 'mouse,disable_multitouch')


from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

import database
from screens.login import LoginScreen
from screens.signup import SignupScreen
from screens.home import HomeScreen
from screens.transaction import TransactionScreen
from screens.admin import AdminScreen
from utils.styles import BACKGROUND


class ATMApp(App):
    title = 'ATM Banking'

    def build(self):
        # user_data_dir is writable on both Android and desktop
        database.init(self.user_data_dir)

        Window.clearcolor = BACKGROUND
        Window.softinput_mode = 'below_target'   # keyboard doesn't hide inputs
        Window.bind(on_keyboard=self._on_keyboard)

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TransactionScreen(name='transactions'))
        sm.add_widget(AdminScreen(name='admin'))
        return sm

    def _on_keyboard(self, window, key, *args):
        """Android back button / Esc key: go back one screen."""
        if key != 27:
            return False
        current = self.root.current
        if current == 'login':
            return False                      # let the app exit
        if current == 'signup':
            self.root.current = 'login'
        elif current == 'transactions':
            self.root.current = 'home'
        elif current == 'home':
            self.root.get_screen('home').ask_logout()
        elif current == 'admin':
            self.root.get_screen('admin').ask_logout()
        return True



import os
import sys

def auto_build_exe():
    """Build build/ and dist/ folders with ATMBanking.exe via PyInstaller when 'build' or '--build' flag is passed."""
    if getattr(sys, 'frozen', False) or platform in ('android', 'ios'):
        return

    if os.environ.get('PYINSTALLER_BUILDING') == '1':
        return

    spec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ATMBanking.spec')
    if os.path.exists(spec_path):
        print("\n=======================================================")
        print("[Auto-Build] Packaging ATMBanking.exe... Please wait.")
        print("=======================================================\n")
        os.environ['PYINSTALLER_BUILDING'] = '1'
        try:
            import shutil
            import subprocess
            subprocess.run([sys.executable, '-m', 'PyInstaller', spec_path, '--noconfirm', '--log-level', 'WARN'], check=False)
            dist_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'ATMBanking.exe')
            desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
            desktop_exe = os.path.join(desktop_dir, 'ATMBanking.exe')
            if os.path.exists(dist_exe) and os.path.exists(desktop_dir):
                shutil.copy2(dist_exe, desktop_exe)
                print(f"[Auto-Build] Updated Desktop shortcut: {desktop_exe}")
            print("\n[Auto-Build] Build complete! ATMBanking.exe created in dist/\n")
        except Exception as e:
            print(f"[Auto-Build] Build error: {e}")
        finally:
            os.environ.pop('PYINSTALLER_BUILDING', None)



if __name__ == '__main__':
    if any(arg in sys.argv for arg in ('build', '--build')):
        auto_build_exe()
    ATMApp().run()

