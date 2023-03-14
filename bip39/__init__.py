"""BIP 39 handling"""

import hashlib
import hmac
import struct
from enum import IntEnum, unique
from typing import List, Optional
from functools import reduce

from util import *


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


# Total number of words
WORDS_LIST_NUM: int = 2048
# Word length in bit
WORD_BIT_LEN: int = 11

SEED_PBKDF2_ROUNDS: int = 2048


def prf(p, s):
    hx = hmac.new(p, msg=s, digestmod=hashlib.sha512)
    return hx.digest()


def link(s, pw, prf):
    s[0], s[1] = s[1], prf(pw, s[1])
    return s[0]


def mnemonics_to_seed(seed: str, passphrase: Optional[str] = None):
    if passphrase is None:
        passphrase = b""
    salt = b"mnemonic" + tobytes(passphrase)

    res = PBKDF2(password=seed, salt=salt, dkLen=64,
                 prf=prf, count=SEED_PBKDF2_ROUNDS)
    return res


def PBKDF2(password, salt, dkLen=16, count=1000, prf=None):
    password = tobytes(password)
    salt = tobytes(salt)

    key = b''
    i = 1
    while len(key) < dkLen:
        s = [prf(password, salt + struct.pack(">I", i))] * 2
        key += reduce(strxor, (link(s, password, prf) for j in range(count)))
        i += 1

    return key[:dkLen]


def validate_checksum(seed: List[str], n_words: Bip39WordsNum) -> bool:
    return False

