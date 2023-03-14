"""UI"""
import curses
from binascii import hexlify
from typing import List

from pick import pick

from bip39 import (
    Bip39WordsNum,
    mnemonics_to_seed,
)
from bip39.data import wordlist

Screen = 'curses._CursesWindow'

prompts = {
    "init": """BIP39-Monero Mnemonic Converter v0.1
Convert your English BIP39 mnemonic into a 25-word Monero mnemonic according to SLIP10. """,
    "anykey": "Press any key to contine.",
    "bip39_length": "How many words are in your BIP39 mnemonic?",
    "bip39_mnem": "Your BIP39 mnemonic: ",
    "bip39_passphrase?": "Do you use a passphrase?",
    "bip39_input_passphrase": "Passphrase: ",


    "end": "If you are done, press enter to quit. All data will be erased.",
}

options = {
    "bip39_length": list(map(int, Bip39WordsNum)),
    "bip39_passphrase?": ["Yes", "No"],
}


def validate(c: str) -> bool:
    return len(c) == 1 and c.isalpha()


def is_enter(c: int) -> bool:
    return c in [curses.KEY_ENTER, 10, 13]


def wait_msg(screen: Screen, prompt: str):
    screen.addstr("\n\n" + prompts[prompt])
    screen.getch()


def wait(screen: Screen):
    wait_msg(screen, "anykey")


def picker(screen: Screen, key: str):
    # selected, ind = pick(options[key], prompts[key], indicator="=>", screen=screen)
    selected, _ = pick(options[key], prompts[key],
                       indicator="=>", screen=screen)
    return selected


def yesno_to_bool(yn: str) -> bool:
    ci = yn.lower()
    return ci in ('yes', 'y')


def read_passphrase(screen: Screen) -> str:
    screen.clear()
    phrase = read_word(
        screen, prompts["bip39_input_passphrase"], 255, passw=True)
    return phrase


def read_word(screen: Screen, prompt: str, maxlen: int = 16,
              passw: bool = False, validate=lambda _: True) -> str:
    l = 0
    word = []
    c = ""
    word_entered = False
    screen.addstr(prompt)
    while not word_entered or l >= maxlen:
        c = screen.getch()
        char = chr(c)
        if is_enter(c):
            word_entered = True
        elif c in (curses.KEY_BACKSPACE, '\x7f'):
            # TODO backspace
            pass
        elif validate(char):
            if passw:
                disp = '*'
            else:
                char = char.lower()
                disp = char
            screen.addch(disp)
            word.append(char)
            l = l + 1
    return ''.join(word)


def advance_line(screen: Screen):
    (my, _) = screen.getmaxyx()
    (y, _) = screen.getyx()
    ny = y + 1
    if ny >= my:
        screen.clear()
        ny = 0
    screen.addstr(ny, 0, '')


def write_ok(screen: Screen, text: str):
    screen.addstr(text, curses.color_pair(1))


def write_err(screen: Screen, text: str):
    screen.addstr(text, curses.color_pair(2))


def read_words(screen: Screen, biplen: int) -> List[str]:
    def validate_word(word: str) -> bool:
        return word in wordlist

    words: List[str] = []
    for n in range(1, biplen + 1):
        word_valid = False
        while not word_valid:
            word = read_word(screen, f"Enter word #{n}/{biplen}: ", 8)
            word_valid = validate_word(word)
            if word_valid:
                write_ok(screen, " OK")
            else:
                write_err(screen, " x")
            advance_line(screen)
        words.append(''.join(word))
        print()

    return words


def program(screen: Screen):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    # UI start
    screen.clear()

    screen.addstr(prompts["init"])
    wait(screen)
    biplen = picker(screen, "bip39_length")

    screen.clear()
    words = read_words(screen, biplen)
    words = read_words("asd", screen)
    bip39phrase = ' '.join(words)
    # bip39phrase: str = ' '.join(["bacon"] * biplen)
    bippass: bool = yesno_to_bool(picker(screen, "bip39_passphrase?"))
    passphrase = None
    if bippass:
        passphrase = read_passphrase(screen)
    screen.clear()
    c = mnemonics_to_seed(bip39phrase, passphrase)
    # screen.addstr("\n")
    screen.addstr(prompts["bip39_mnem"])
    screen.addstr(bip39phrase)
    screen.addstr("\n")
    screen.addstr(hexlify(c))

    wait_msg(screen, "end")
