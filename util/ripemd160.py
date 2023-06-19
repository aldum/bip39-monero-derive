### Lifted from https://github.com/hasnainroopawalla/hashbase/

from typing import Any, List

# rotate_left, modular_add, apply_message_padding

def rotate_left(x: int, s: int, size: int = 32) -> int:
    """Circular rotation of x left by s bit positions.

    Args:
        x (int): The input integer.
        s (int): The number of shifts (in bits).
        size (int): The size of the input/output in bits.

    Returns:
        int: The left rotated value of the input integer.
    """
    z = 0xFFFFFFFF if size == 32 else 0xFFFFFFFFFFFFFFFF
    return ((x << s) | (x >> (size - s))) & z


def modular_add(nums: List[int], size: int = 32) -> int:
    """Performs modular addition of all elements in nums, modulo 2^32.

    Args:
        nums (List[int]): A List of all the input integers.
        size (int): The size of the input/output in bits.

    Returns:
        int: The value obtained after modular addition of all elements in nums.
    """
    z = 0xFFFFFFFF if size == 32 else 0xFFFFFFFFFFFFFFFF
    return sum(nums) & z


def apply_message_padding(
    message: bytearray,
    message_length_byteorder: Any,
    message_length_padding_bits: int = 64,
    message_chunk_size_bits: int = 512,
) -> bytearray:
    """Pre-processing for the input message.
    Appends a trailing '1'.
    Pad 0s to the message.
    Append message length to the message in little or big endian.

    Args:
        message (bytearray): The input message in bytes.
        message_length_byteorder (str): Can be either 'big' or 'little', indicating if the last
                64 bits of the message (message length) are in the big or little endian convention.
        message_length_padding_bits (int): The number of bits to be appended at the end of the
                message chunk to indicate the length of the original message.
        message_chunk_size_bits (int): The size of the message chunk in bits.

    Returns:
        bytearray: The pre-processed message in bytes.
    """
    # Store the length of the message in bits
    original_message_length_in_bits = len(message) * 8

    # Pad a trailing '1'
    message.append(0x80)

    # Pad 0s to assert a block length of (message_chunk_size_bits-message_length_padding_bits) bits
    while (
        len(message) * 8 + message_length_padding_bits
    ) % message_chunk_size_bits != 0:
        message.append(0)

    # Pad the last message_length_padding_bits bits that indicate the message length in the
    #   specified endian format
    message += (original_message_length_in_bits).to_bytes(
        message_length_padding_bits // 8, byteorder=message_length_byteorder
    )

    return message


class RIPEMD160:
    """The RIPEMD-160 algorithm is a cryptographic hashing function used to produce a 160-bit hash.
    https://homes.esat.kuleuven.be/~bosselae/ripemd/rmd160.txt
    """

    def __init__(self) -> None:
        self.h0: int = 0x67452301
        self.h1: int = 0xEFCDAB89
        self.h2: int = 0x98BADCFE
        self.h3: int = 0x10325476
        self.h4: int = 0xC3D2E1F0
        self.K: List[int] = (
            [0x00000000] * 16
            + [0x5A827999] * 16
            + [0x6ED9EBA1] * 16
            + [0x8F1BBCDC] * 16
            + [0xA953FD4E] * 16
        )
        self.K_C: List[int] = (
            [0x50A28BE6] * 16
            + [0x5C4DD124] * 16
            + [0x6D703EF3] * 16
            + [0x7A6D76E9] * 16
            + [0x00000000] * 16
        )
        self.R = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8, 3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12, 1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2, 4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]  # noqa: E501
        self.R_C = [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12, 6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2, 15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13, 8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14, 12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]  # noqa: E501

        self.SHIFTS = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8, 7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12, 11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5, 11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12, 9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]  # noqa: E501
        self.SHIFTS_C = [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6, 9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11, 9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5, 15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8, 8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]  # noqa: E501

    @staticmethod
    def split_message_block_into_words(
        message_block: bytearray, word_length_in_bytes: int = 4
    ) -> List[int]:
        """Split the 64-byte message block into 16 4-byte words.

        Args:
            message_block (bytearray): The 512-bytes message block.
            word_length_in_bytes (int, optional): The length of each word in the block. Default 4.

        Returns:
            List[int]: A List of 4-byte words created by splitting the message block.
        """
        return [
            int.from_bytes(
                message_block[4 * i : 4 * i + word_length_in_bytes], byteorder="little"
            )
            for i in range(len(message_block) // word_length_in_bytes)
        ]

    @staticmethod
    def F(j: int, x: int, y: int, z: int) -> int:
        if 0 <= j & j < 16:
            f = x ^ y ^ z
        if 16 <= j & j < 32:
            f = (x & y) | (z & ~x)
        if 32 <= j & j < 48:
            f = (~y | x) ^ z
        if 48 <= j & j < 64:
            f = (x & z) | (y & ~z)
        if 64 <= j & j < 80:
            f = x ^ (y | ~z)
        return f

    def register_values_to_hex_string(self) -> str:
        """Read the values of the 5 registers and convert them to a hexadecimal string.

        Returns:
            str: The hexadecimal string represented by the 5 registers.
        """
        digest = sum(
            register_value << (32 * i)
            for i, register_value in enumerate(
                [self.h0, self.h1, self.h2, self.h3, self.h4]
            )
        )
        return digest.to_bytes(20, byteorder="little").hex()

    def calculate_hash(self, message_in_bytes: bytearray) -> str:
        message_chunk = apply_message_padding(message_in_bytes, "little")

        # Loop through each 64-byte message block
        for block in range(len(message_chunk) // 64):
            message_words = self.split_message_block_into_words(
                message_chunk[block * 64 : block * 64 + 64]
            )
            a, b, c, d, e = self.h0, self.h1, self.h2, self.h3, self.h4
            a_c, b_c, c_c, d_c, e_c = self.h0, self.h1, self.h2, self.h3, self.h4

            for j in range(80):
                w = modular_add(
                    [a, self.F(j, b, c, d), message_words[self.R[j]], self.K[j]]
                )
                t = modular_add([rotate_left(w, self.SHIFTS[j]), e])
                a, e, d, c, b = e, d, rotate_left(c, 10), b, t

                w = modular_add(
                    [
                        a_c,
                        self.F(79 - j, b_c, c_c, d_c),
                        message_words[self.R_C[j]],
                        self.K_C[j],
                    ]
                )
                t = modular_add([rotate_left(w, self.SHIFTS_C[j]), e_c])
                a_c, e_c, d_c, c_c, b_c = e_c, d_c, rotate_left(c_c, 10), b_c, t

            t = modular_add([self.h1, c, d_c])
            self.h1 = modular_add([self.h2, d, e_c])
            self.h2 = modular_add([self.h3, e, a_c])
            self.h3 = modular_add([self.h4, a, b_c])
            self.h4 = modular_add([self.h0, b, c_c])
            self.h0 = t

        return self.register_values_to_hex_string()



    def generate_hash(self, message: str) -> str:
        """Generates a 160-bit RIPEMD-160 hash of the input message.

        Args:
            message (str): The input message/text.

        Returns:
            str: The 160-bit RIPEMD-160 hash of the message.
        """
        message_in_bytes = bytearray(message, "ascii")
        return self.calculate_hash(message_in_bytes)
