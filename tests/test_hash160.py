import unittest

from util import hash160, hash160_hashlib

class TestUtils(unittest.TestCase):
    def test_strxor(self):
        b = b'\x01\x02\x03\x04'

        self.assertEqual(hash160(b), hash160_hashlib(b))
