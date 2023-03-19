from enum import IntEnum, unique
from typing import List, Literal
from binascii import crc32, unhexlify

from util import IntegerUtils, BytesUtils
from .data import wordlist

n = wordlist.WORDS_LIST_NUM


def byteschunk_to_words(bytes_chunk: bytes,
                        endianness: Literal["little", "big"]) -> List[str]:
    """
        Get words from a bytes chunk.

        Args:
            bytes_chunk (bytes)                  : Bytes chunk
            endianness ("big" or "little")       : Bytes endianness

        Returns:
            list[str]: 3 word indexes
        """
    int_chunk = BytesUtils.to_integer(bytes_chunk, endianness=endianness)

    word1_idx = int_chunk % n
    word2_idx = ((int_chunk // n) + word1_idx) % n
    word3_idx = ((int_chunk // n // n) + word2_idx) % n

    return [wordlist[w] for w in (word1_idx, word2_idx, word3_idx)]


@unique
class MoneroEntropyBitLen(IntEnum):
    """Enumerative for Monero entropy bit lengths."""

    BIT_LEN_128 = 128
    BIT_LEN_256 = 256


ENTROPY_BIT_LEN: List[MoneroEntropyBitLen] = [
    MoneroEntropyBitLen.BIT_LEN_128,
    MoneroEntropyBitLen.BIT_LEN_256,
]


def _is_valid_entropy_len(entropy_byte_len: bytes) -> bool:
    return entropy_byte_len * 8 in ENTROPY_BIT_LEN


def encode(entropy_bytes: bytes) -> List[str]:
    """
    Encode bytes to list of mnemonic words.

    Args:
        entropy_bytes (bytes): Entropy bytes (accepted lengths in bits: 128, 256)

    Returns:
        list[str]: List of encoded mnemonic words

    Raises:
        ValueError: If bytes length is not valid
    """
    # Check entropy length
    entropy_byte_len = len(entropy_bytes)
    if not _is_valid_entropy_len(entropy_byte_len):
        raise ValueError(
            f"Entropy byte length ({entropy_byte_len}) is not valid")

    # Consider 4 bytes at a time, 4 bytes represent 3 words
    mnemonic = []
    for i in range(len(entropy_bytes) // 4):
        mnemonic += byteschunk_to_words(
            entropy_bytes[i * 4:(i * 4) + 4], "little")

    return mnemonic


def encode_int(seed: int) -> List[str]:
    return encode(IntegerUtils.to_bytes(seed))

# def encode_int(seed: int) -> str:
#     hexstr = IntegerUtils.to_binary_str(seed)
#     return encode(hexstr)


# def encode(hexstr) -> str:
#     """Convert hexadecimal string to mnemonic word representation with checksum."""
#     out = []
#     for i in range(len(hexstr) // 8):
#         part = hexstr[8 * i: 8 * i + 8]
#         word = endian_swap(part)
#         x = int(word, 16)
#         w1 = x % n
#         w2 = (x // n + w1) % n
#         w3 = (x // n // n + w2) % n
#         out += [wordlist[w1], wordlist[w2], wordlist[w3]]
#     checksum = get_checksum(" ".join(out))
#     out.append(checksum)
#     return " ".join(out)


def decode(phrase: List[str]) -> str:
    """Calculate hexadecimal representation of the phrase."""
    phrase = phrase.split(" ")
    out = ""

    for i in range(len(phrase) // 3):
        word1, word2, word3 = phrase[3 * i: 3 * i + 3]
        w1 = wordlist.get_word_idx(word1)
        w2 = wordlist.get_word_idx(word2) % n
        w3 = wordlist.get_word_idx(word3) % n
        x = w1 + n * ((w2 - w1) % n) + n * \
            n * ((w3 - w2) % n)
        # out += f"%08{x}"
        out += endian_swap(f"%08{x}")
    return out


def endian_swap(word: str) -> str:
    """Given any string, swap bits and return the result.

    :rtype: str
    """
    return "".join([word[i: i + 2] for i in [6, 4, 2, 0]])


def get_checksum(phrase: List[str]):
    """Given a mnemonic word string, return a string of the computed checksum.

    :rtype: str
    """
    phrase_split = phrase.split(" ")
    if len(phrase_split) < 12:
        raise ValueError("Invalid mnemonic phrase")
    if len(phrase_split) > 13:
        # Standard format
        phrase = phrase_split[:24]
    else:
        # MyMonero format
        phrase = phrase_split[:12]
    wstr = "".join(word[: wordlist.unique_prefix_length] for word in phrase)
    wstr = bytearray(wstr.encode("utf-8"))
    z = ((crc32(wstr) & 0xFFFFFFFF) ^ 0xFFFFFFFF) >> 0
    z2 = ((z ^ 0xFFFFFFFF) >> 0) % len(phrase)
    return phrase_split[z2]
