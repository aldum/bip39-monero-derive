"""Utility functions"""


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






def strxor(s1: bytes, s2: bytes) -> bytes:
    l = len(s1)
    ret = bytearray(l)
    for i in range(0, l):
        ret[i] = s1[i] ^ s2[i]
    return ret
