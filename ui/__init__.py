"""UI"""

from slip0010.sd import SeedDerivation
from bip39.data import wordlist
from bip39 import (
    Bip39WordsNum,
    validate_checksum,
)
from util.debug import (
    get_debug,
    set_debug_screen,
)
from typing import (
    Dict,
    List,
    Optional,
)

from ui.input import Input, Screen
from ui.pick import pick
from util.screen import (
    advance_line,
    yesno_to_bool,
    bool_to_yesno,
    fit_output,
    fit_err_output,
    fit_info_output,
    break_output_screen,
    check_dimensions,
    setup_colors,
    write_err,
    write_info,
    write_ok,
)

DEBUG: bool = False
if get_debug():
    DEBUG = True


version = "0.1.0"


def _bip39_word(n: int, s: int) -> str:
    return f"Enter word #{n:02}/{s}: "


def _bip39_word_invalid(w: str) -> str:
    return f"Invalid word. Try again. ({w})"


prompts: Dict[str, str] = {
    "anykey": "Press any key to contine.",
    "blurb": f"BIP39-Monero Mnemonic Converter v{version}",
    "tagline": "Convert your English BIP39 mnemonic into a 25-word Monero mnemonic according to SLIP10.",  # noqa: E501
    "quit_notice": "You can quit any time by pressing Escape.",
    "warning": "WARNING: Make sure you understand why you are doing this. Consult the README.md before you continue.",  # noqa: E501
    "git_url": "https://github.com/aldum/bip39-monero-derive/blob/master/README.md",
    "bip39_length": "How many words are in your BIP39 mnemonic?",
    "bip39_info": "Full and shortened BIP39 words (first four letters) are both accepted.",
    "bip39_invalid": "Invalid mnemonic. Try again. ",
    "bip39_valid": "Mnemonic OK. ",
    "bip39_mnem": "Your BIP39 mnemonic: ",
    "bip39_passphrase?": "Do you use a passphrase?",
    "bip39_input_passphrase": "Passphrase: ",
    "bip39_confirm_passphrase": "Confirm passphrase: ",
    "bip39_passphrase_mismatch": "The passphrases don't match! Try again.",
    "monero_mnem": "Your derived Monero mnemonic: ",
    "nuke": "Esc pressed, exiting.",
    "end": "If you are done, press enter to quit. All data will be erased.",
}


def _break(screen: Screen, s: str) -> str:
    return break_output_screen(screen, s)


def _get_initial_prompt(screen: Screen) -> str:
    return f"""{prompts["blurb"]}

{_break(screen, f"{prompts['tagline']}")}
{_break(screen, f"{prompts['quit_notice']}")}

{_break(screen, f"{prompts['warning']}")}
{prompts["git_url"]}


{prompts["bip39_length"]}"""


options: Dict[str, List[str]] = {
    "bip39_length": list(map(str, map(int, Bip39WordsNum))),
    "bip39_passphrase?": ["Yes", "No"],
}


def validate(c: str) -> bool:
    return len(c) == 1 and c.isalpha()


def wait_msg(screen: Screen, prompt: Optional[str] = None):
    if prompt is not None:
        screen.addstr("\n\n")
        screen.addstr(f"{prompts[prompt]}\n")
    screen.getch()


def wait_enter(screen: Screen, prompt: str):
    screen.addstr("\n\n")
    fit_output(screen, f"{prompts[prompt]}")
    word_entered = False
    while not word_entered:
        try:
            key = Input.read_input(screen)
            if key and (key.is_enter() or key.is_Esc()):
                word_entered = True
        except AttributeError:
            pass


def wait(screen: Screen):
    wait_msg(screen, "anykey")


def picker(screen: Screen, key: str) -> str:
    return _picker(screen, options[key], f"{prompts[key]}")


def picker_prompt(screen: Screen, optsKey: str, prompt: str) -> str:
    return _picker(screen, options[optsKey], prompt)


def _picker(screen: Screen, opts: List[str], prompt: str) -> str:
    # selected, ind = pick(options[key], prompts[key], "=>", screen)
    ret = pick(opts, prompt, indicator="=>", screen=screen, wraparaound=False)
    if ret is None:
        raise KeyboardInterrupt
    selected, _ = ret
    return selected


def read_passphrase(screen: Screen) -> str:
    screen.clear()
    matching = False
    while not matching:
        phrase = read_word(
            screen, f"{prompts['bip39_input_passphrase']}", passw=True
        )
        advance_line(screen)
        confirm = read_word(
            screen, f"{prompts['bip39_confirm_passphrase']}", passw=True
        )
        matching = phrase == confirm
        if not matching:
            advance_line(screen)
            fit_err_output(screen, f"{prompts['bip39_passphrase_mismatch']}")
            advance_line(screen)
    return phrase


def read_word(
    screen: Screen, prompt: str, passw: bool = False, validate=lambda _: True
) -> str:
    (y, _) = screen.getyx()
    word = []
    disp_word = []
    clear: bool = False

    def add_char(ch: str) -> None:
        if passw:
            disp_word.append("*")
        else:
            disp_word.append(ch)
        word.append(ch)

    word_entered = False
    while not word_entered:
        screen.addstr(y, 0, prompt)
        screen.addstr("".join(disp_word))

        if clear:
            screen.clrtoeol()
            clear = False

        key = Input.read_input(screen, wide=passw)
        if key is None:
            continue
        if key.is_Esc():
            raise KeyboardInterrupt
        if key.isalpha:
            if validate(key.char):
                char = key.char or ""
                if not passw:
                    char = (char or "").lower()
                add_char(char)
        if key.is_enter():
            word_entered = True
        if key.is_space():
            if not passw:
                word_entered = True
            else:
                add_char(" ")
        if key.is_bksp():
            word = word[:-1]
            disp_word = disp_word[:-1]
            screen.addstr("".join(disp_word))
            clear = True

    return "".join(word)


def read_words(screen: Screen, biplen: int) -> List[str]:
    screen.addstr("\n\n")
    words: List[str] = []
    for n in range(1, biplen + 1):
        word_valid: bool = False
        word_prefix: bool = False
        full_word: str = ""
        while not word_valid:
            prompt: str = _bip39_word(n, biplen)
            word: str = read_word(screen, prompt)

            # TODO clean this up
            if (
                len(word) == wordlist.unique_prefix_length
                and word in wordlist.unique_prefixes
                and not wordlist.contains(full_word)
            ):
                full_word = wordlist.unique_prefixes[word]
                word_prefix = True
            else:
                full_word = word
            word_valid = wordlist.contains(full_word)
            if not word_valid:
                screen.addstr(" ")
                write_err(screen, _bip39_word_invalid(word))
            if word_prefix:
                write_info(screen, f" ({full_word})")
            advance_line(screen)

        words.append("".join(full_word))

    return words


def _endscreen(
    screen: Screen, sd: SeedDerivation, bip39_phrase: str, has_pass: bool
) -> None:
    screen.addstr("\n")
    fit_info_output(screen, f"{prompts['bip39_mnem']}")
    screen.addstr("\n\n")
    fit_info_output(screen, bip39_phrase)
    screen.addstr("\n\n")
    write_info(screen, "Passphrase: " + bool_to_yesno(has_pass))
    screen.addstr("\n\n")
    screen.addstr(f"{prompts['monero_mnem']}")
    screen.addstr("\n\n")
    fit_output(screen, sd.electrum_words)
    screen.addstr("\n\n")
    wait_enter(screen, "end")


def program(screen: Screen) -> bool:
    if not check_dimensions(screen):
        raise AssertionError("We need a bigger terminal")
    set_debug_screen(screen, DEBUG)
    setup_colors()

    screen.clear()

    if DEBUG:
        biplen = Bip39WordsNum(12)
    else:
        prompt = _get_initial_prompt(screen)
        biplen = Bip39WordsNum(
            int(picker_prompt(screen, "bip39_length", prompt))
        )

    screen.clear()
    mnem_valid = False

    fit_output(screen, f"{prompts['bip39_info']}")
    while not mnem_valid:
        if DEBUG:
            # bip39_phrase: str = ' '.join(["bacon"] * biplen)
            # words: List[str] = ["bacon"] * biplen
            # 'coach someone found provide arch ritual outside spike unit enter margin warm'
            mnem = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"  # noqa: E501 # pylint: disable=C0301
            words: List[str] = mnem.split(" ")
        else:
            words = read_words(screen, biplen)
        mnem_valid = validate_checksum(words, biplen)
        if not mnem_valid:
            write_err(screen, f"{prompts['bip39_invalid']}")
            screen.addstr("\n")
        else:
            write_ok(screen, f"{prompts['bip39_valid']}")

    bip39_phrase = " ".join(words)

    bippass: bool = False
    passphrase = ""
    bippass = yesno_to_bool(picker(screen, "bip39_passphrase?"))
    if bippass:
        passphrase = read_passphrase(screen)

    sd = SeedDerivation.derive_monero(bip39_phrase, passphrase)
    screen.clear()
    _endscreen(screen, sd, bip39_phrase, bippass)

    return True


def bye():
    print(prompts["nuke"])
