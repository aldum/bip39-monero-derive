from enum import IntEnum, unique
from typing import List, Literal
from binascii import crc32, hexlify

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


def mn_encode(message: bytes, checksum=False) -> List[str]:
    def mn_swap_endian_4byte(st):
        # this is from moneromoo's code
        r = st[6:8] + st[4:6] + st[2:4] + st[0:2]
        return r

    def checksum_create(wlist, unique_prefix_len=wordlist.unique_prefix_length):
        acc = ""
        for w in wlist:
            acc += w[:unique_prefix_len] if len(w) > unique_prefix_len else w

        acc = acc.encode("utf8")
        crc = crc32(acc) & 0xFFFFFFFF
        return crc % len(wlist)

    out = []
    n = wordlist.WORDS_LIST_NUM
    message = hexlify(message)
    for i in range(0, len(message), 8):
        message = (
            message[0:i] +
            mn_swap_endian_4byte(message[i: i + 8]) + message[i + 8:]
        )

    for i in range(len(message) // 8):
        word = message[8 * i: 8 * i + 8]
        x = int(word, 16)
        w1 = x % n
        w2 = ((x // n) + w1) % n
        w3 = (((x // n) // n) + w2) % n
        word1 = wordlist[w1]
        word2 = wordlist[w2]
        word3 = wordlist[w3]
        out += [word1, word2, word3]

    if checksum:
        idx = checksum_create(out)
        out.append(out[idx])
    return out


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
    entropy_byte_len = bytes(len(entropy_bytes))
    if not _is_valid_entropy_len(entropy_byte_len):
        raise ValueError(
            f"Entropy byte length ({entropy_byte_len!r}) is not valid")

    # Consider 4 bytes at a time, 4 bytes represent 3 words
    mnemonic = []
    BL = 4
    for i in range(len(entropy_bytes) // BL):
        mnemonic += byteschunk_to_words(
            entropy_bytes[i * BL:(i * BL) + BL], "little")
        # entropy_bytes[i * BL:(i * BL) + BL], "big")

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
    # phrase = phrase.split(" ")
    out = ""

    for i in range(len(phrase) // 3):
        word1, word2, word3 = phrase[3 * i: 3 * i + 3]
        w1 = wordlist.get_word_idx_unsafe(word1)
        w2 = wordlist.get_word_idx_unsafe(word2) % n
        w3 = wordlist.get_word_idx_unsafe(word3) % n
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


def get_checksum(phrase_split: List[str]) -> str:
    """Given a mnemonic word string, return a string of the computed checksum.

    :rtype: str
    """

    if len(phrase_split) < 12:
        raise ValueError("Invalid mnemonic phrase")
    if len(phrase_split) > 13:
        # Standard format
        phrase = phrase_split[:24]
    else:
        # MyMonero format
        phrase = phrase_split[:12]
    wstr = "".join(word[: wordlist.unique_prefix_length] for word in phrase)
    wstr_bytes = bytearray(wstr.encode("utf-8"))
    z = ((crc32(wstr_bytes) & 0xFFFFFFFF) ^ 0xFFFFFFFF) >> 0
    z2 = ((z ^ 0xFFFFFFFF) >> 0) % len(phrase)
    return phrase_split[z2]
