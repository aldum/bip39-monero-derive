import unittest

from hypothesis import assume, given  # type: ignore
from hypothesis import strategies as st

import Crypto.Util.strxor as ref  # type: ignore

from util import (
    strxor,
    IntegerUtils as I,
    BytesUtils as B,
)

blists = st.lists(st.sampled_from(["0", "1"]))
two_binaries = st.integers(min_value=0, max_value=10).flatmap(
    lambda i: st.tuples(
        st.binary(min_size=i, max_size=i), st.binary(min_size=i, max_size=i)
    )
)


class TestUtils(unittest.TestCase):
    @given(two_binaries)
    def test_strxor(self, tup):
        (b1, b2) = tup
        self.assertEqual(strxor(b1, b2), ref.strxor(b1, b2))


class TestIntegerUtils(unittest.TestCase):
    def test_to_bstr(self):
        self.assertEqual(I.to_binary_str(0), "0")
        self.assertEqual(I.to_binary_str(0, 2), "00")
        self.assertEqual(I.to_binary_str(1), "1")
        self.assertEqual(I.to_binary_str(1, 2), "01")

    def test_from_bstr(self):
        self.assertEqual(I.from_binary_str("0"), 0)
        self.assertEqual(I.from_binary_str("1"), 1)

    @given(st.integers(min_value=0))
    def test_from_inverts_to(self, i):
        print(i)
        assert I.from_binary_str(I.to_binary_str(i)) == i

    @given(blists)
    def test_to_inverts_from(self, bl):
        bs = "".join(bl)
        assume(bs)  # filter empties
        # converting to int to account for leading zeros
        self.assertEqual(
            int(I.to_binary_str(I.from_binary_str(bs)), 2), int(bs, 2)
        )


class TestBytesUtils(unittest.TestCase):
    def test_to_bstr(self):
        self.assertEqual(B.to_binary_str((0).to_bytes(1, byteorder="big")), "0")
        self.assertEqual(B.to_binary_str((1).to_bytes(1, byteorder="big")), "1")
        self.assertEqual(
            B.to_binary_str((4).to_bytes(1, byteorder="big")), "100"
        )


if __name__ == "__main__":
    unittest.main()
