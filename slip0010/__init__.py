import hmac
from hashlib import sha512
from binascii import hexlify
from typing import Tuple

from util import IntegerUtils


def derive_monero_master_key(seed) -> Tuple[int, bytes]:
    curve = b"ed25519 seed"
    I = hmac.new(curve, msg=seed, digestmod=sha512).digest()
    I_L, chain_code = I[:32], I[32:]
    key = int.from_bytes(I_L, "big")
    return (key, chain_code)
