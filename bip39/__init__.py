"""BIP 39 handling"""

import hashlib
from hashlib import sha256
import hmac
import struct
import unicodedata
from enum import IntEnum, unique
from typing import List
from functools import reduce

from util import (
    to_bytes,
    strxor,
    BytesUtils,
    IntegerUtils,
)
from bip39.data import wordlist


@unique
class Bip39WordsNum(IntEnum):
    """Enumerative for BIP39 words number."""

    WORDS_NUM_12 = 12
    WORDS_NUM_15 = 15
    WORDS_NUM_18 = 18
    WORDS_NUM_21 = 21
    WORDS_NUM_24 = 24

    ''' |  ENT  | CS | ENT+CS |  MS  |
        +-------+----+--------+------+
        |  128  |  4 |   132  |  12  |
        |  160  |  5 |   165  |  15  |
        |  192  |  6 |   198  |  18  |
        |  224  |  7 |   231  |  21  |
        |  256  |  8 |   264  |  24  |
        '''

    def get_checksum_len(self) -> int:
        ms_to_cs = {
            12: 4,
            15: 5,
            18: 6,
            21: 7,
            24: 8,
        }
        return ms_to_cs[self]


# Word length in bit
WORD_BIT_LEN: int = 11

SEED_PBKDF2_ROUNDS: int = 2048


def link(s, pw, prf):
    s[0], s[1] = s[1], prf(pw, s[1])
    return s[0]


def mnemonics_to_seed(seed, passphrase=b""):
    salt = b"mnemonic" + passphrase

    def prf(p, s):
        hx = hmac.new(p, msg=s, digestmod=hashlib.sha512)
        return hx.digest()

    res = PBKDF2(password=seed, salt=salt, dkLen=64, prf=prf, count=2048)
    return res


def PBKDF2(password, salt, dkLen=16, count=1000, prf=None) -> bytes:
    password = to_bytes(password)
    salt = to_bytes(salt)

    key = b''
    i = 1
    while len(key) < dkLen:
        s = [prf(password, salt + struct.pack(">I", i))] * 2
        key += reduce(strxor, (link(s, password, prf) for j in range(count)))
        i += 1

    return key[:dkLen]


def validate_checksum(seed: List[str], n_words: Bip39WordsNum) -> bool:
    # __MnemonicToBinaryStr
    def get_bytes(word: str) -> str:
        wOpt = wordlist.get_word_idx_option(word)
        if wOpt:
            return IntegerUtils.to_binary_str(wOpt, WORD_BIT_LEN)
        return ''
    mnemonic_bin_str_m = map(get_bytes, seed)
    mnemonic_bin_str: str = ''.join(mnemonic_bin_str_m)

    checksum_len: int = Bip39WordsNum(n_words).get_checksum_len()
    checksum_bin_str = mnemonic_bin_str[-checksum_len:]
    # checksum_bin_str_got = self.__ComputeChecksumBinaryStr(mnemonic_bin_str)
    # __ComputeChecksumBinaryStr
    #       __EntropyBytesFromBinaryStr
    entropy_bin_str = mnemonic_bin_str[:-checksum_len]
    entropy_bytes = BytesUtils.from_binary_str(
        entropy_bin_str, checksum_len * 8)
    #          return
    dig = sha256()
    dig.update(entropy_bytes)
    digest = dig.digest()
    digest_size = dig.digest_size
    entropy_hash_bin_str = BytesUtils.to_binary_str(digest, digest_size * 8)

    checksum_bin_str_computed = entropy_hash_bin_str[:checksum_len]

    return checksum_bin_str == checksum_bin_str_computed


def normalize_NFKD(data_str: str) -> str:
    """
    Normalize string using NFKD.

    Args:
        data_str (str): Input string

    Returns:
        str: Normalized string
    """
    return unicodedata.normalize("NFKD", data_str)
