"""Utility functions"""


def b(s):
    # utf-8 would cause some side-effects we don't want
    return s.encode("latin-1")


def bchr(s):
    return bytes([s])


def bstr(s):
    if isinstance(s, str):
        return bytes(s, "latin-1")
    else:
        return bytes(s)


def bord(s):
    return s


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


def tostr(bs) -> str:
    return bs.decode("latin-1")


def byte_string(s) -> bool:
    return isinstance(s, bytes)


def strxor(s1: bytes, s2: bytes) -> bytes:
    l = len(s1)
    ret = bytearray(l)
    for i in range(0, l):
        ret[i] = s1[i] ^ s2[i]
    return ret
