"""Reusable styled widgets: Card, Text, RoundedButton, StyledInput, Header, popups."""
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from utils.styles import (
    ACCENT, BORDER, CURRENCY, GRAY_BTN, GREEN, INPUT_BG, PRIMARY, RED,
    TEXT_DARK, TEXT_MUTED, TEXT_ON_DARK_MUTED, WHITE,
)


class Card(BoxLayout):
    """A BoxLayout with a rounded, coloured background."""
    bg_color = ListProperty(WHITE)
    radius = ListProperty([0])

    def __init__(self, **kwargs):
        kwargs.setdefault('radius', [dp(16)])
        super().__init__(**kwargs)
        # pyrefly: ignore [missing-attribute]
        with self.canvas.before:
            self._tint = Color(*self.bg_color)
            # pyrefly: ignore [missing-attribute]
            self._shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self._redraw, size=self._redraw,
                  bg_color=self._redraw, radius=self._redraw)

    def _redraw(self, *args):
        self._tint.rgba = self.bg_color
        # pyrefly: ignore [missing-attribute]
        self._shape.pos = self.pos
        # pyrefly: ignore [missing-attribute]
        self._shape.size = self.size
        self._shape.radius = self.radius


class Text(Label):
    """Label with sensible defaults: left aligned, fixed height, wraps to its size."""

    def __init__(self, **kwargs):
        kwargs.setdefault('color', TEXT_DARK)
        kwargs.setdefault('font_size', sp(16))
        kwargs.setdefault('halign', 'left')
        kwargs.setdefault('valign', 'middle')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(28))
        super().__init__(**kwargs)
        self.bind(size=self._fit)
        self._fit()

    def _fit(self, *args):
        # pyrefly: ignore [missing-attribute]
        self.text_size = self.size


class RoundedButton(Button):
    """Flat rounded button that darkens while pressed."""
    bg_color = ListProperty(PRIMARY)
    radius = ListProperty([0])

    def __init__(self, **kwargs):
        kwargs.setdefault('radius', [dp(12)])
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        kwargs.setdefault('font_size', sp(16))
        kwargs.setdefault('bold', True)
        kwargs.setdefault('color', WHITE)
        kwargs['background_normal'] = ''
        kwargs['background_down'] = ''
        kwargs['background_color'] = (0, 0, 0, 0)
        super().__init__(**kwargs)
        # pyrefly: ignore [missing-attribute]
        with self.canvas.before:
            self._tint = Color(*self.bg_color)
            # pyrefly: ignore [missing-attribute]
            self._shape = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self._redraw, size=self._redraw, bg_color=self._redraw,
                  radius=self._redraw, state=self._redraw)
        self._redraw()

    def _redraw(self, *args):
        r, g, b, a = self.bg_color
        # pyrefly: ignore [missing-attribute]
        shade = 0.78 if self.state == 'down' else 1.0
        self._tint.rgba = (r * shade, g * shade, b * shade, a)
        # pyrefly: ignore [missing-attribute]
        self._shape.pos = self.pos
        # pyrefly: ignore [missing-attribute]
        self._shape.size = self.size
        self._shape.radius = self.radius


class StyledInput(TextInput):
    """Rounded text field with a highlight border when focused."""

    def __init__(self, **kwargs):
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(50))
        kwargs.setdefault('font_size', sp(16))
        kwargs.setdefault('padding', [dp(16), dp(14), dp(16), dp(14)])
        super().__init__(
            background_normal='', background_active='',
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT_DARK, hint_text_color=TEXT_MUTED,
            cursor_color=PRIMARY, write_tab=False, **kwargs)
        # pyrefly: ignore [missing-attribute]
        with self.canvas.before:
            Color(*INPUT_BG)
            # pyrefly: ignore [missing-attribute]
            self._fill = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            self._edge_color = Color(*BORDER)
            # pyrefly: ignore [missing-attribute]
            self._edge = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                              width=dp(1.2))
        self.bind(pos=self._redraw, size=self._redraw, focus=self._redraw)

    def _redraw(self, *args):
        # pyrefly: ignore [missing-attribute]
        self._fill.pos = self.pos
        # pyrefly: ignore [missing-attribute]
        self._fill.size = self.size
        # pyrefly: ignore [missing-attribute]
        self._edge.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(12))
        self._edge_color.rgba = ACCENT if self.focus else BORDER


class Header(Card):
    """Dark blue header with rounded bottom corners (login / signup)."""

    def __init__(self, title, subtitle='', badge=True, height=dp(220), **kwargs):
        super().__init__(
            orientation='vertical', bg_color=PRIMARY,
            radius=[0, 0, dp(36), dp(36)],
            size_hint_y=None, height=height,
            padding=[dp(20), dp(24), dp(20), dp(20)], spacing=dp(6), **kwargs)
        self.add_widget(Widget())
        if badge:
            circle = Card(bg_color=ACCENT, radius=[dp(32)], size_hint=(None, None),
                          size=(dp(64), dp(64)), pos_hint={'center_x': 0.5})
            circle.add_widget(Text(text=CURRENCY, font_size=sp(34), bold=True, color=WHITE,
                                   halign='center', size_hint_y=1))
            self.add_widget(circle)
        self.add_widget(Text(text=title, font_size=sp(26), bold=True, color=WHITE,
                             halign='center', height=dp(34)))
        if subtitle:
            self.add_widget(Text(text=subtitle, font_size=sp(14), color=TEXT_ON_DARK_MUTED,
                                 halign='center', height=dp(22)))
        self.add_widget(Widget())


def show_popup(title, message, kind='info', on_confirm=None, on_close=None):
    """Styled popup. kind: 'info' | 'success' | 'error'.
    If on_confirm is given, shows NO / YES buttons and calls it on YES."""
    color = {'info': PRIMARY, 'success': GREEN, 'error': RED}.get(kind, PRIMARY)

    content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(14))
    content.add_widget(Text(text=message, halign='center', size_hint_y=1))

    row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
    if on_confirm:
        no_btn = RoundedButton(text='NO', bg_color=GRAY_BTN, height=dp(48))
        no_btn.bind(on_release=lambda *_: popup.dismiss())
        yes_btn = RoundedButton(text='YES', bg_color=color, height=dp(48))

        def _yes(*_):
            popup.dismiss()
            on_confirm()
        yes_btn.bind(on_release=_yes)
        row.add_widget(no_btn)
        row.add_widget(yes_btn)
    else:
        ok_btn = RoundedButton(text='OK', bg_color=color, height=dp(48))
        ok_btn.bind(on_release=lambda *_: popup.dismiss())
        row.add_widget(ok_btn)
    content.add_widget(row)

    popup = Popup(
        title=title, content=content,
        size_hint=(0.88, None), size_hint_max_x=dp(420), height=dp(240),
        background='', background_color=WHITE,
        title_color=color, title_size=sp(18), title_align='center',
        separator_color=color)
    if on_close:
        def _closed(*_):
            on_close()
        popup.bind(on_dismiss=_closed)
    popup.open()
    return popup