"""Colour palette and small formatting helpers."""
from kivy.utils import get_color_from_hex as hx

PRIMARY = hx('#1A237E')
PRIMARY_LIGHT = hx('#3949AB')
ACCENT = hx('#448AFF')
GREEN = hx('#2E9D5B')
RED = hx('#E53935')
ORANGE = hx('#FB8C00')
GRAY_BTN = hx('#78909C')

WHITE = hx('#FFFFFF')
BACKGROUND = hx('#F2F4F8')
CHIP_BG = hx('#E3E8FF')
INPUT_BG = hx('#FFFFFF')
BORDER = hx('#CFD4E3')

TEXT_DARK = hx('#212121')
TEXT_MUTED = hx('#757575')
TEXT_ON_DARK_MUTED = hx('#C5CAE9')

CURRENCY = '\u20b9'          # change to 'Rs.' if your font shows a box
MAX_AMOUNT = 10_000_000


def money(value):
    return f'{CURRENCY}{value:,.2f}'