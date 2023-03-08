import curses
from curses import wrapper

from pick import pick


# SCREEN = {}

prompts = {
    "init": """BIP39-Monero Mnemonic Converter v0.1
Convert your English BIP39 mnemonic into a 25-word Monero mnemonic according to SLIP10. """,
    "anykey": "Press any key to contine.",
    "bip39_length": "How many words are in your BIP39 mnemonic?",
    "bip39_mnem": "Your BIP39 mnemonic: ",
    "bip39_passphrase?": "Do you use a passphrase?",
    "end": "If you are done, press enter to quit. All data will be erased.",
}
options = {
    "bip39_length": [12, 15, 18, 21, 24],
    "bip39_passphrase?": ["Yes", "No"],
}


def program(screen):
    def wait(prompt: str = "anykey"):
        screen.addstr("\n\n" + prompts[prompt])
        screen.getch()

    def picker(key: str):
        # selected, ind = pick(options[key], prompts[key], indicator="=>", screen=screen)
        selected, _ = pick(options[key], prompts[key], indicator="=>", screen=screen)

        return selected

    def validate(c: str) -> bool:
        return len(c) == 1 and c.isalpha()

    def is_enter(c: int) -> bool:
        return c in [curses.KEY_ENTER, 10, 13]

    # UI start
    screen.clear()

    screen.addstr(prompts["init"])
    wait()
    biplen = picker("bip39_length")

    screen.clear()

    words = []
    for n in range(1, biplen + 1 - 10):
        word = []
        c = ""
        screen.addstr(n, 0, f"Enter word #{n}: ")
        word_entered = False
        while not word_entered:
            c = screen.getch()
            char = chr(c)
            if validate(char):
                screen.addch(char)
                word.append(char.lower())
            elif is_enter(c):
                word_entered = True

        words.append(''.join(word))
        print()
        (_, y) = curses.getsyx()
        curses.setsyx(0, y)

    screen.clear()
    bip39phrase = ' '.join(words)
    screen.addstr(prompts["bip39_mnem"])
    screen.addstr(bip39phrase)
    # bippass = picker("bip39_passphrase?")

    wait("end")


def __main__():
    wrapper(program)


__main__()
