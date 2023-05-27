import hmac
from hashlib import sha512
from typing import Tuple, Union

from util import err_print


def encode(data: Union[bytes, str],
           encoding: str = "utf-8") -> bytes:
    if isinstance(data, str):
        return data.encode(encoding)
    if isinstance(data, bytes):
        return data
    raise TypeError("Invalid data type")


PUB_KEY_BYTE_LEN = 32

_Q = 2 ** 255 - 19


def _inv(x: int) -> int:
    return pow(x, _Q - 2, _Q)


_D = -121665 * _inv(121666)
_I = pow(2, (_Q - 1) // 4, _Q)  # noqa: E741


def _x_recover(y: int) -> int:
    xx = (y * y - 1) * _inv(_D * y * y + 1)
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


def derive_monero_master_key(seed: bytes) -> Tuple[bytes, bytes]:
    # def int_decode(b: bytes) -> int:
    #     return BytesUtils.to_integer(b, endianness="little")

    # def point_decode_no_check(point_bytes: bytes) -> Tuple[int, int]:
    #     # if not point_is_encoded_bytes(point_bytes):
    #     #     raise ValueError("Invalid point bytes")

    #     point_int = int_decode(point_bytes)

    #     clamp = (1 << 255) - 1
    #     y = point_int & clamp
    #     x = _x_recover(y)
    #     if bool(x & 1) != bool(point_int & (1 << 255)):
    #         x = _Q - x

    #     return x, y

    # def point_bytes_to_coord(point_bytes: bytes) -> Tuple[int, int]:
    #     if len(point_bytes) == 64:
    #         return int_decode(point_bytes[:32]), int_decode(point_bytes[32:])
    #     if len(point_bytes) == 32:
    #         return point_decode_no_check(point_bytes)
    #     raise ValueError("Invalid point bytes")

    # def point_is_on_curve(point: Union[bytes, Tuple[int, int]]) -> bool:
    #     if isinstance(point, bytes):
    #         point = point_bytes_to_coord(point)

    #     x = point[0]
    #     y = point[1]
    #     return (-x * x + y * y - 1 - _D * x * x * y * y) % _Q == 0

    # def is_valid_bytes(key_bytes: bytes) -> bool:
    #     PUB_KEY_PREFIX: bytes = b"\x00"
    #     if (len(key_bytes) == 32 + len(PUB_KEY_PREFIX)
    #             and key_bytes[0] == BytesUtils.to_integer(PUB_KEY_PREFIX)):
    #         key_bytes = key_bytes[1:]

    #     if not point_is_on_curve(key_bytes):
    #         return False
    #     return True

    curve = b'ed25519 seed'
    # seed = hexlify(seed)
    err_print(f"in {type(seed)!r}, {seed!r}")
    I = hmac.new(curve, msg=seed, digestmod=sha512).digest() # noqa: E741
    key, chain_code = I[:32], I[32:]
    # I_L, chain_code = I[:32], I[32:]
    # err_print(f"I_L {I_L} {hexlify(I_L)}`")
    # key = int.from_bytes(I_L, "big")
    # key = int.from_bytes(I_L, "little")
    return (key, chain_code)

    # hmac_half_len = 32
    # hmac_r = b""
    # hmac_data = seed
    # success = False

    # while not success:
    #     hmac_r = hmac.digest(encode(curve), encode(hmac_data), "sha512")
    #     err_print(f"hmmac {hexlify(hmac_r)}")
    #     # If private key is not valid, the new HMAC data is the current HMAC
    #     success = is_valid_bytes(hmac_r[:hmac_half_len])
    #     if not success:
    #         hmac_data = hmac_r

    # I_L, I_R = hmac_r[:hmac_half_len], hmac_r[hmac_half_len:]
    # return (int.from_bytes(I_L, "big"), I_R)
