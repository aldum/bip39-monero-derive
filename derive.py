"""Interactive application for deriving a Monero mnemonic from a BIP 39 seedphrase."""

from curses import wrapper
import ui


def __main__():
    try:
        wrapper(ui.program)
    except KeyboardInterrupt:
        print("Bye.")


__main__()
