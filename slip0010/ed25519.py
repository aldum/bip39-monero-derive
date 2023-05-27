import binascii
from typing import Tuple

from slip0010 import ed25519_2
from slip0010 import keccak2

b = 256
q = 2 ** 255 - 19
l = 2 ** 252 + 27742317777372353535851937790883648493 # noqa: E741


def _offset(x, offset=0):
    if offset == 0:
        return x
    return x[offset:]


def bit(h, i):
    return ((h[i // 8]) >> (i % 8)) & 1


def decodeint(s):
    return sum(2 ** i * bit(s, i) for i in range(0, b))


def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    return bytes(
        [(sum([bits[i * 8 + j] << j for j in range(8)]))
         for i in range(b // 8)]
    )


def identity(byte_enc=False):
    """
    Identity point
    :return:
    """
    idd = EdPoint()
    return idd if not byte_enc else bytes(idd)


def encodepoint(P):
    return bytes(P)


def decodepoint(b, offset=0):
    return EdPoint(_offset(b, offset))


def scalarmult_base(a):
    if isinstance(a, EdScalar):
        return EdPoint(ed25519_2.scalarmult_B(a.v))
    if isinstance(a, int):
        return EdPoint(ed25519_2.scalarmult_B(a))


def point_eq(P, Q):
    P.check() and Q.check()
    return P == Q


_decodeint = decodeint
_encodeint = encodeint
_encodepoint = ed25519_2.encodepoint
_decodepoint = ed25519_2.decodepoint


class EdScalar(object):
    def __init__(self, v=None, offset=0):
        self.v = 0
        self.init(v, offset)

    def init(self, src=None, offset=0):
        if src is None:
            self.v = 0
        elif isinstance(src, int):
            self.v = src % l
        elif isinstance(src, EdScalar):
            self.v = src.v
        else:
            self.v = _decodeint(src[offset:]) % l
        return self

    def _assert_scalar(self, other):
        if not isinstance(other, EdScalar):
            raise ValueError("operand is not EdScalar")

    def __repr__(self):
        t = binascii.hexlify(_encodeint(self.v))
        return f"EdScalar({t})"

    # def __cmp__(self, other):
    #     if isinstance(other, int):
    #         return cmp(self.v, other)
    #     if not isinstance(other, EdScalar):
    #         raise ValueError("Neither EdScalar nor integer")
    #     return cmp(self.v, other.v)

    def __eq__(self, other):
        self._assert_scalar(other)
        return self.v == other.v

    def __bytes__(self):
        return _encodeint(self.v)

    def modinv(self):
        self.v = pow(self.v, l - 2, l)
        return self

    def __neg__(self):
        return EdScalar(-1 * self.v)

    def __add__(self, other):
        self._assert_scalar(other)
        return EdScalar(self.v + other.v)

    def __sub__(self, other):
        return EdScalar(self.v - other.v)

    def __mul__(self, other):
        return EdScalar(self.v * other.v)

    @classmethod
    def ensure_scalar(cls, x):
        if isinstance(x, EdScalar):
            return x
        return EdScalar(x)


class EdPoint(object):
    def __init__(self, v=None, offset=0):
        self.v = ed25519_2.ident
        self.init(v, offset)

    def init(self, src=None, offset=0):
        if src is None:
            self.v = ed25519_2.ident
        elif isinstance(src, EdPoint):
            self.v = src.v
        elif isinstance(src, tuple):
            self.v = src
        else:
            self.v = _decodepoint(src[offset:])
        return self

    def __repr__(self):
        return "EdPoint(%r)" % binascii.hexlify(_encodepoint(self.v))

    def __getitem__(self, item):
        return self.v[item]

    # def __eq__(self, other):
    #     if isinstance(other, EdPoint):
    #         return ed25519ietf.point_equal(self.v, other.v)
    #     elif isinstance(other, tuple):
    #         return ed25519ietf.point_equal(self.v, other)
    #     else:
    #         ValueError("Neither EdPoint nor quadruple")

    def __bytes__(self):
        return _encodepoint(self.v)

    def check(self):
        if not ed25519_2.isoncurve(self.v):
            raise ValueError("P is not on ed25519 curve")

    @staticmethod
    def invert_v(v):
        return -1 * v[0] % q, v[1], v[2], -1 * v[3] % q

    def invert(self):
        self.v = EdPoint.invert_v(self.v)
        return self

    def _assert_point(self, other):
        if not isinstance(other, EdPoint):
            raise ValueError("operand is not EdPoint")

    def __add__(self, other):
        self._assert_point(other)
        return EdPoint(ed25519_2.edwards_add(self.v, other.v))

    def __neg__(self):
        return EdPoint(self).invert()

    def __sub__(self, other):
        self._assert_point(other)
        return EdPoint(ed25519_2.edwards_add(self.v, EdPoint.invert_v(other.v)))

    def __mul__(self, other):
        return EdPoint(ed25519_2.scalarmult(self.v, other.v))


Ge25519 = EdPoint
Sc25519 = EdScalar


def generate_keys(recovery_key):
    """
    Wallet gen.
    :param recovery_key:
    :return:
    """
    pub = scalarmult_base(recovery_key)
    return recovery_key, pub


def generate_monero_keys(seed: Sc25519) -> Tuple[Sc25519, Ge25519]:
    """
    Generates spend key / view key from the seed in the same manner as Monero code does.

    account.cpp:
    crypto::secret_key account_base::generate(
        const crypto::secret_key& recovery_key,
        bool recover, bool two_random).
    :param seed:
    :return:
    """
    spend_sec, spend_pub = generate_keys(_decodeint(seed))
    # hash = cn_fast_hash(_encodeint(spend_sec))
    # view_sec, view_pub = generate_keys(_decodeint(hash))
    return spend_sec, spend_pub  # , view_sec, view_pub


def cn_fast_hash(buff):
    """
    Keccak 256, original one (before changes made in SHA3 standard)
    :param buff:
    :return:
    """
    kc2 = keccak2.Keccak256()
    kc2.update(buff)
    return kc2.digest()
