"""UI"""
import curses
from typing import List
from binascii import hexlify

from pick import pick

from bip39 import (
    Bip39WordsNum,
    mnemonics_to_seed,
    validate_checksum,
)
from bip39.data import (
    wordlist,
    wordlist_contains,
    MAX_WORDLEN,
)
from monero import encode_int
from slip0010 import derive_monero_master_key


Screen = 'curses._CursesWindow'

prompts = {
    "init": """BIP39-Monero Mnemonic Converter v0.1
Convert your English BIP39 mnemonic into a 25-word Monero mnemonic according to SLIP10. """,
    "anykey": "Press any key to contine.",
    "bip39_length": "How many words are in your BIP39 mnemonic?",
    "bip39_word_invalid": "Invalid word. Try again. ",
    "bip39_invalid": "Invalid mnemonic. Try again. ",
    "bip39_valid": "Mnemonic OK. ",
    "bip39_mnem": "Your BIP39 mnemonic: ",
    "bip39_passphrase?": "Do you use a passphrase?",
    "bip39_input_passphrase": "Passphrase: ",

    "monero_mnem": "The derived Monero mnemonic: ",


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
    screen.addstr("\n\n" + prompts[prompt] + "\n")
    screen.getch()


def wait_enter(screen: Screen, prompt: str):
    screen.addstr("\n\n" + prompts[prompt])
    word_entered = False
    while not word_entered:
        c = screen.getch()
        if is_enter(c):
            word_entered = True


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
    if ny >= my - 1:
        screen.clear()
        ny = 0
    screen.addstr(ny, 0, '')


def write_ok(screen: Screen, text: str):
    _write_color(screen, text, 1)


def write_err(screen: Screen, text: str):
    _write_color(screen, text, 2)


def _write_color(screen: Screen, text: str, pair: int):
    # (y, _) = screen.getyx()
    # screen.addstr(f"{text} {y}", curses.color_pair(1))
    screen.addstr(text, curses.color_pair(pair))


def read_words(screen: Screen, biplen: int) -> List[str]:
    words: List[str] = []
    for n in range(1, biplen + 1):
        word_valid: bool = False
        while not word_valid:
            word = read_word(
                screen, f"Enter word #{n}/{biplen}: ", MAX_WORDLEN)
            word_valid = wordlist_contains(word)
            screen.addstr('\n')
            if word_valid:
                write_ok(screen, "OK. ")
            else:
                write_err(screen, prompts["bip39_word_invalid"])
            advance_line(screen)

        words.append(''.join(word))
        print()

    return words


def program(screen: Screen):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    # UI start
    screen.clear()

    DEBUG = False
    # DEBUG = True
    screen.addstr(prompts["init"])
    wait(screen)
    if DEBUG:
        biplen = 12
    else:
        biplen = picker(screen, "bip39_length")

    screen.clear()
    mnem_valid = False

    while not mnem_valid:
        if DEBUG:
            # bip39_phrase: str = ' '.join(["bacon"] * biplen)
            # words: List[str] = ["bacon"] * biplen
            words: List[str] = \
                'coach someone found provide arch ritual outside spike unit enter margin warm' \
                .split(' ')
        else:
            words = read_words(screen, biplen)
        mnem_valid = True
        mnem_valid = validate_checksum(words, biplen)
        if not mnem_valid:
            write_err(screen, prompts["bip39_invalid"])
            screen.addstr("\n")
        else:
            write_ok(screen, prompts["bip39_valid"])
        wait(screen)
    bip39_phrase = ' '.join(words)

    bippass: bool = False
    passphrase = None
    if not DEBUG:
        yesno_to_bool(picker(screen, "bip39_passphrase?"))
        if bippass:
            passphrase = read_passphrase(screen)

    screen.clear()
    screen.addstr("\n")
    screen.addstr(prompts["bip39_mnem"])
    screen.addstr("\n")
    screen.addstr("\n")
    screen.addstr(bip39_phrase)
    screen.addstr("\n")
    seed: bytes = mnemonics_to_seed(bip39_phrase, passphrase)
    (monero_key, _chain_code) = derive_monero_master_key(seed)
    screen.addstr("\n")
    screen.addstr(prompts["monero_mnem"])
    screen.addstr("\n\n")
    mnem_words: List[str] = encode_int(monero_key)
    SPLIT = 6
    for i in range(len(mnem_words) // SPLIT):
        chunk = mnem_words[i * SPLIT:(i * SPLIT) + SPLIT]
        screen.addstr(' '.join(chunk))
        screen.addstr("\n")

    wait_enter(screen, "end")
