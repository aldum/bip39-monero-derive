"""BIP 39 handling"""

import hashlib
import hmac
import struct
from enum import IntEnum, unique
from typing import Optional
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
