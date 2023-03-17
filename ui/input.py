import curses
from curses import ascii as asc
from typing import Optional, Literal, Union

Screen = 'curses._CursesWindow'

Char = Union[str, int]


class Input:
    Special = Literal['esc', 'enter', 'backspace', 'del', 'space']

    empty: bool = False
    char: Optional[str] = None
    control: Optional[str] = None
    special: Optional[Special] = None
    isalpha: bool = False

    def __init__(self, got: Optional[Char]):
        if got is None:
            self.empty = True
            return

        self.control = asc.unctrl(got)
        if got in ["\x08", 263, '\x97']:
            self.special = 'backspace'
        elif got in ["\x20", ' ']:
            self.special = 'space'
        elif got == "\x1b":
            self.special = 'esc'
        elif got == "\x0a":
            self.special = 'enter'
        elif got in ["\x7f", 330]:
            self.special = 'del'
        elif asc.isgraph(got):
            ch = got
            if isinstance(got, int):
                ch = chr(got)
            self.char = ch
            self.control = None
            if asc.isalpha(ch):
                self.isalpha = True

    def is_Esc(self) -> bool:
        return self.special == 'esc'

    def is_enter(self) -> bool:
        return self.special == 'enter'

    def is_space(self) -> bool:
        return self.special == 'space'

    def is_bksp(self) -> bool:
        return self.special == 'backspace'

    @staticmethod
    def get_empty():
        return Input(None)

    @staticmethod
    def read_input(screen: Screen) -> Optional['Input']:
        try:
            key: Char = screen.get_wch()
            # screen.addstr(f"got: {key} {type(key)}\n")
            return Input(key)

        except curses.error:
            return None
