"""Interactive application for deriving a Monero mnemonic from a BIP 39 seedphrase."""
import signal
from curses import wrapper
import ui


def __main__():
    def handler(_sig, _handler):
        print("Ctrl+C pressed.")

    # Set the signal handler
    signal.signal(signal.SIGINT, handler)

    wrapper(ui.program)


__main__()
