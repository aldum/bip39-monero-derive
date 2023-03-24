"""Utility functions"""
import os
import signal
import curses
import hashlib
from sys import stderr
from typing import Union, List, Literal, Optional
from hashlib import sha256
from binascii import unhexlify
from functools import wraps


Screen = 'curses._CursesWindow'
DEBUG: bool
__DBG_SCREEN: Screen


def to_bytes(s: Union[bytes, bytearray, str, memoryview],
             encoding="latin-1"):
    if isinstance(s, bytes):
        return s
    if isinstance(s, bytearray):
        return bytes(s)
    if isinstance(s, str):
        return s.encode(encoding)
    if isinstance(s, memoryview):
        return s.tobytes()
    return bytes([s])


class IntegerUtils:
    """Class container for integer utility functions."""

    @staticmethod
    def encode(data: Union[bytes, str],
               encoding: str = "utf-8") -> bytes:
        """
        Encode to bytes.

        Args:
            data (str or bytes): Data
            encoding (str)     : Encoding type

        Returns:
            bytes: String encoded to bytes

        Raises:
            TypeError: If the data is neither string nor bytes
        """
        if isinstance(data, str):
            return data.encode(encoding)
        if isinstance(data, bytes):
            return data

    @staticmethod
    def to_bytes(data_int: int,
                 bytes_num: Optional[int] = None,
                 endianness: Literal["little", "big"] = "big",
                 signed: bool = False) -> bytes:
        """
        Convert integer to bytes.

        Args:
            data_int (int)                          : Data integer
            bytes_num (int, optional)               : Number of bytes, automatic if None
            endianness ("big" or "little", optional): Endianness (default: big)
            signed (bool, optional, default: false) : True if signed, false otherwise

        Returns:
            bytes: Bytes representation
        """

        # In case gmpy is used
        if data_int.__class__.__name__ == "mpz":
            data_int = int(data_int)

        bytes_num = bytes_num or (
            (data_int.bit_length() if data_int > 0 else 1) + 7) // 8
        return data_int.to_bytes(bytes_num, byteorder=endianness, signed=signed)

    @staticmethod
    def from_binary_str(data: Union[bytes, str]) -> int:
        """
        Convert the specified binary string to integer.

        Args:
            data (str or bytes): Data

        Returns:
            int: Integer representation
        """
        return int(IntegerUtils.encode(data), 2)

    @staticmethod
    def to_binary_str(data_int: int,
                      zero_pad_bit_len: int = 0) -> str:
        """
            Convert the specified integer to a binary string.

            Args:
                data_int (int)                  : Data integer
                zero_pad_bit_len (int, optional): Zero pad length in bits, 0 if not specified

            Returns:
                str: Binary string
            """
        return bin(data_int)[2:].zfill(zero_pad_bit_len)


class BytesUtils:
    """Class container for bytes utility functions."""

    @staticmethod
    def to_binary_str(data_bytes: bytes,
                      zero_pad_bit_len: int = 0) -> str:
        """
        Convert the specified bytes to a binary string.

        Args:
            data_bytes (bytes)              : Data bytes
            zero_pad_bit_len (int, optional): Zero pad length in bits, 0 if not specified

        Returns:
            str: Binary string
        """
        return IntegerUtils.to_binary_str(BytesUtils.to_integer(data_bytes), zero_pad_bit_len)

    @staticmethod
    def to_integer(data_bytes: bytes,
                   endianness: Literal["little", "big"] = "big",
                   signed: bool = False) -> int:
        """
        Convert the specified bytes to integer.

        Args:
            data_bytes (bytes)                      : Data bytes
            endianness ("big" or "little", optional): Endianness (default: big)
            signed (bool, optional, default: false) : True if signed, false otherwise

        Returns:
            int: Integer representation
        """
        return int.from_bytes(data_bytes, byteorder=endianness, signed=signed)

    @staticmethod
    def from_binary_str(data: Union[bytes, str],
                        zero_pad_byte_len: int = 0) -> bytes:
        """
        Convert the specified binary string to bytes.

        Args:
            data (str or bytes)              : Data
            zero_pad_byte_len (int, optional): Zero pad length in bytes, 0 if not specified

        Returns:
            bytes: Bytes representation
        """
        return unhexlify(
            hex(int(BytesUtils.encode(data), 2))[2:].zfill(zero_pad_byte_len)
        )

    @staticmethod
    def encode(data: Union[bytes, str],
               encoding: str = "utf-8") -> bytes:
        """
        Encode to bytes.

        Args:
            data (str or bytes): Data
            encoding (str)     : Encoding type

        Returns:
            bytes: String encoded to bytes

        Raises:
            TypeError: If the data is neither string nor bytes
        """
        if isinstance(data, str):
            return data.encode(encoding)
        if isinstance(data, bytes):
            return data
        raise TypeError("Invalid data type")


def strxor(s1: bytes, s2: bytes) -> bytes:
    l = len(s1)
    ret = bytearray(l)
    for i in range(0, l):
        ret[i] = s1[i] ^ s2[i]
    return ret


def err_print(s: str):
    print(s, file=stderr)


def set_debug_screen(screen: Screen, debug: bool) -> None:
    global __DBG_SCREEN  # pylint: disable=W0603
    __DBG_SCREEN = screen
    global DEBUG  # pylint: disable=W0603
    DEBUG = debug


def scr_debug_print(s: str) -> None:
    if DEBUG:
        s = str(s)
        screen = __DBG_SCREEN
        (y, x) = screen.getyx()
        (_, mx) = screen.getmaxyx()
        slack = mx - x
        clear = ' ' * slack
        l = len(s)
        pad = 2
        padded = l + 2 * pad
        if padded <= slack:
            __DBG_SCREEN.addstr(clear)
            # __DBG_SCREEN.addstr(y, x + 3, s, curses.color_pair(3))
            __DBG_SCREEN.addstr(y, mx - l - pad, s, curses.color_pair(3))
            __DBG_SCREEN.move(y, x)


def handler(sig, _handler):
    if sig == signal.SIGINT:
        print("Ctrl+C pressed.")


def catch_sigint():
    signal.signal(signal.SIGINT, handler)


def lower_escdelay():
    os.environ.setdefault('ESCDELAY', '25')


def get_debug():
    dbg = os.environ.get('DEBUG')
    if dbg in [1, '1', 'true', 'y']:
        return True
    return False


def memoize(f):
    """Memoization decorator for a function taking one or more arguments."""

    def _c(*args, **kwargs):
        if not hasattr(f, "cache"):
            f.cache = {}
        key = (args, tuple(kwargs))
        if key not in f.cache:
            f.cache[key] = f(*args, **kwargs)
        return f.cache[key]

    return wraps(f)(_c)


def hash160(data):
    """Return ripemd160(sha256(data))"""
    rh = hashlib.new("ripemd160", sha256(data).digest())
    return rh.digest()
