import curses

from . import Screen


def yesno_to_bool(yn: str) -> bool:
    ci = yn.lower()
    return ci in ('yes', 'y')


def bool_to_yesno(b: bool) -> str:
    if b:
        return 'yes'
    return 'no'


def fit_output(screen: Screen, s: str) -> None:
    screen.addstr(break_output_screen(screen, s))


def fit_err_output(screen: Screen, s: str) -> None:
    text = break_output_screen(screen, s)
    write_err(screen, text)


def fit_info_output(screen: Screen, s: str) -> None:
    text = break_output_screen(screen, s)
    write_info(screen, text)


def advance_line(screen: Screen):
    (my, _) = screen.getmaxyx()
    (y, _) = screen.getyx()
    ny = y + 1
    if ny >= my - 1:
        screen.clear()
        ny = 0
    screen.addstr(ny, 0, '')


def break_output(s: str, mx: int = 70) -> str:
    words = s.split(' ')
    broken = []
    line = ''
    for w in words:
        wl = len(w)
        ll = len(line)
        if ll + 1 + wl <= mx:
            line = f'{line} {w}'
        else:
            broken.append(line.strip())
            line = w
    broken.append(line.strip())
    return '\n'.join(broken)


def break_output_screen(screen: Screen, s: str) -> str:
    # assuming full line as target
    (_, mx) = screen.getmaxyx()
    return break_output(s, mx - 1)


def check_dimensions(screen: Screen) -> bool:
    (my, mx) = screen.getmaxyx()
    return mx >= 70 and my >= 20


def setup_colors() -> None:
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)


def write_ok(screen: Screen, text: str):
    _write_color(screen, text, 1)


def write_err(screen: Screen, text: str):
    _write_color(screen, text, 2)


def write_info(screen: Screen, text: str):
    screen.addstr(text, curses.A_DIM)
    # _write_color(screen, text, 3)


def _write_color(screen: Screen, text: str, pair: int):
    screen.addstr(text, curses.color_pair(pair))
