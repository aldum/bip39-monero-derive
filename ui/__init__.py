"""UI"""
import curses
from curses import ascii as asc
from typing import List, Optional
from binascii import hexlify

from ui.input import Input, Screen
from ui.pick import pick
from bip39 import (
    Bip39WordsNum,
    mnemonics_to_seed,
    validate_checksum,
)
from bip39.data import wordlist
from monero import encode_int
from slip0010 import derive_monero_master_key


_initPrompt = """BIP39-Monero Mnemonic Converter v0.1
Convert your English BIP39 mnemonic into a 25-word Monero mnemonic according to SLIP10. """

prompts = {
    "init": _initPrompt,
    "anykey": "Press any key to contine.",
    # "bip39_length": "How many words are in your BIP39 mnemonic?",
    "bip39_length": f"""{_initPrompt}\n\nHow many words are in your BIP39 mnemonic?""",
    "bip39_word": lambda n, s: f"Enter word #{n:02}/{s}: ",
    "bip39_word_invalid": lambda w = '': f"Invalid word. Try again. ({w})",
    "bip39_invalid": "Invalid mnemonic. Try again. ",
    "bip39_valid": "Mnemonic OK. ",
    "bip39_mnem": "Your BIP39 mnemonic: ",
    "bip39_passphrase?": "Do you use a passphrase?",
    "bip39_input_passphrase": "Passphrase: ",

    "monero_mnem": "Your derived Monero mnemonic: ",


    "nuke": "Esc pressed, exiting.",
    "end": "If you are done, press enter to quit. All data will be erased.",
}

options = {
    "bip39_length": list(map(int, Bip39WordsNum)),
    "bip39_passphrase?": ["Yes", "No"],
}


def validate(c: str) -> bool:
    return len(c) == 1 and c.isalpha()


def wait_msg(screen: Screen, prompt: Optional[str] = None):
    if prompt is not None:
        screen.addstr("\n\n" + prompts[prompt] + "\n")
    screen.getch()


def wait_enter(screen: Screen, prompt: str):
    screen.addstr("\n\n" + prompts[prompt])
    word_entered = False
    while not word_entered:
        key = Input.read_input(screen)
        if key.is_enter() or key.is_Esc():
            word_entered = True


def wait(screen: Screen):
    wait_msg(screen, "anykey")


def picker(screen: Screen, key: str):
    return _picker(screen, options[key], prompts[key])


def _picker(screen: Screen, opts: List[str], prompt: str):
    # selected, ind = pick(options[key], prompts[key], "=>", screen)
    selected, _ = pick(opts, prompt, indicator="=>", screen=screen)
    return selected


def yesno_to_bool(yn: str) -> bool:
    ci = yn.lower()
    return ci in ('yes', 'y')


def read_passphrase(screen: Screen) -> str:
    screen.clear()
    phrase = read_word(screen, prompts["bip39_input_passphrase"], passw=True)
    return phrase


def read_word(screen: Screen, prompt: str,
              passw: bool = False, validate=lambda _: True) -> str:
    (y, _) = screen.getyx()
    word = []
    disp_word = []

    def add_char(ch: str) -> None:
        if passw:
            disp_word.append('*')
        else:
            disp_word.append(ch)
        word.append(ch)

    word_entered = False
    while not word_entered:
        screen.addstr(y, 0, prompt)
        screen.addstr(''.join(disp_word))
        screen.clrtoeol()
        key = Input.read_input(screen)
        if key.is_Esc():
            raise KeyboardInterrupt
        if key.isalpha:
            if validate(key.char):
                char = key.char.lower()
                add_char(char)
        if key.is_enter():
            word_entered = True
        if key.is_space():
            if not passw:
                word_entered = True
            else:
                add_char(' ')
        if key.is_bksp():
            word = word[:-1]
            disp_word = disp_word[:-1]
            screen.addstr(''.join(disp_word))

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
            word: str = read_word(screen, prompts["bip39_word"](n, biplen))
            word_valid = wordlist.contains(word)
            if not word_valid:
                screen.addstr(' ')
                write_err(screen, prompts["bip39_word_invalid"](word))
            # else:
            #     write_ok(screen, "OK. ")
            advance_line(screen)

        words.append(''.join(word))

    return words


def program(screen: Screen):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    screen.clear()

    DEBUG: bool = False
    # DEBUG = True
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

    bip39_phrase = ' '.join(words)

    bippass: bool = False
    passphrase = None
    bippass = yesno_to_bool(picker(screen, "bip39_passphrase?"))
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


def bye():
    print(prompts["nuke"])
