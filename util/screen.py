
from . import Screen


def yesno_to_bool(yn: str) -> bool:
    ci = yn.lower()
    return ci in ('yes', 'y')


def bool_to_yesno(b: bool) -> str:
    if b:
        return 'yes'
    return 'no'


def fit_output(screen: Screen, s: str) -> None:
    screen.addstr(break_output(screen, s))


def break_output(screen: Screen, s: str) -> str:
    # assuming full line as target
    (_, mx) = screen.getmaxyx()
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


def check_dimensions(screen: Screen) -> bool:
    (my, mx) = screen.getmaxyx()
    return mx >= 70 and my >= 20
