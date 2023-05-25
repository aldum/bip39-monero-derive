import os
import curses

from . import Screen
# from .debug import DEBUG

__DBG_SCREEN: Screen

DEBUG: bool

def get_debug():
    dbg = os.environ.get('DEBUG')
    if dbg in [1, '1', 'true', 'y']:
        return True
    return False


def set_debug_screen(screen: Screen, debug: bool) -> None:
    global __DBG_SCREEN  # pylint: disable=W0603
    __DBG_SCREEN = screen
    global DEBUG  # pylint: disable=W0603
    DEBUG = debug


def scr_debug_print(s: str) -> None:
    if DEBUG:
        s = str(s)
        screen = __DBG_SCREEN
        (y, x) = screen.getyx()
        (_, mx) = screen.getmaxyx()
        slack = mx - x
        clear = ' ' * slack
        tl = len(s)
        pad = 2
        padded = tl + 2 * pad
        if padded <= slack:
            __DBG_SCREEN.addstr(clear)
            # __DBG_SCREEN.addstr(y, x + 3, s, curses.color_pair(3))
            __DBG_SCREEN.addstr(y, mx - tl - pad, s, curses.color_pair(3))
            __DBG_SCREEN.move(y, x)
