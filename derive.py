"""Interactive application for deriving a Monero mnemonic from a BIP 39 seedphrase."""
from curses import wrapper
import ui
from util import catch_sigint, lower_escdelay


def __main__():
    catch_sigint()
    lower_escdelay()

    try:
        wrapper(ui.program)
    except KeyboardInterrupt:
        ui.bye()
    except AssertionError as e:
        print(e)


__main__()
