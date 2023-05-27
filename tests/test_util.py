import unittest

import Crypto.Util.strxor as ref # type: ignore
from hypothesis import assume, given
from hypothesis import strategies as st

from util import strxor, IntegerUtils as I


class TestUtils(unittest.TestCase):
    def test_strxor(self):
        b1 = b'\x01\x02'
        b2 = b'\x03\x04'
        self.assertEqual(strxor(b1, b2), ref.strxor(b1, b2))

class TestIntegerUtils(unittest.TestCase):
    def test_to_bstr(self):
        self.assertEqual(I.to_binary_str(0), '0')
        self.assertEqual(I.to_binary_str(0, 2), '00')
        self.assertEqual(I.to_binary_str(1), '1')
        self.assertEqual(I.to_binary_str(1, 2), '01')

    def test_from_bstr(self):
        self.assertEqual(I.from_binary_str('0'), 0)
        self.assertEqual(I.from_binary_str('1'), 1)

    @given(st.integers(min_value=0))
    def test_from_inverts_to(self, i):
        print(i)
        assert I.from_binary_str(I.to_binary_str(i)) == i

    @given(st.lists(st.sampled_from(['0','1'])))
    def test_to_inverts_from(self, bl):
        bs = ''.join(bl)
        assume(bs) # filter empties
        # converting to int to account for leading zeros
        assert int(I.to_binary_str(I.from_binary_str(bs)), 2) == int(bs, 2)


if __name__ == '__main__':
    unittest.main()
