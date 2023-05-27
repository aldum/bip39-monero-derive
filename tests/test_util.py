import unittest

import Crypto.Util.strxor as ref # type: ignore

from util import strxor


class TestUtils(unittest.TestCase):
    def test_strxor(self):
        b1 = b'\x01\x02'
        b2 = b'\x03\x04'
        self.assertEqual(strxor(b1, b2), ref.strxor(b1, b2))


if __name__ == '__main__':
    unittest.main()
