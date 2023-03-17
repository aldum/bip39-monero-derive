"""Interactive application for deriving a Monero mnemonic from a BIP 39 seedphrase."""
from curses import wrapper
import ui
from util import catch_sigint


def __main__():
    catch_sigint()

    try:
        wrapper(ui.program)
    except KeyboardInterrupt:
        print("Bye.")


__main__()
