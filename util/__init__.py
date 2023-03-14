"""Utility functions"""
from typing import Union, Literal
from binascii import unhexlify


def tobytes(s, encoding="latin-1"):
    if isinstance(s, bytes):
        return s
    elif isinstance(s, bytearray):
        return bytes(s)
    elif isinstance(s, str):
        return s.encode(encoding)
    elif isinstance(s, memoryview):
        return s.tobytes()
    else:
        return bytes([s])


def int_to_binary_str(data_int: int,
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
        return int_to_binary_str(BytesUtils.to_integer(data_bytes), zero_pad_bit_len)

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
