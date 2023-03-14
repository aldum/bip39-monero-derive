import unittest

import Crypto.Util.strxor as ref

from __init__ import (strxor, tobytes)  # disable=E0611


class TestUtils(unittest.TestCase):
    def test_strxor(self):
        b1 = b'0x01x02'
        b2 = b'0x03x04'
        self.assertEqual(strxor(b1, b2), ref.strxor(b1, b2))


if __name__ == '__main__':
    unittest.main()
