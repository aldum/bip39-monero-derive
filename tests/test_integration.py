# pylint: disable=C0301
# import unittest
import unittest
from unittest import TestCase
from binascii import hexlify

from util import err_print
from tests.util import JSONUtils
from slip0010 import sd


class TestUtils(TestCase):
    test_data = []

    def __init__(self, test_name):
        super().__init__(test_name)
        self.test_data = JSONUtils.load_vectors_from_file(
            'tests/test_vectors.json')

    def test_integration(self):
        for l in self.test_data:
            ent = l.entropy
            mnem = l.monero_mnem
            der = sd.SeedDerivation.derive_monero(l.bip39, l.passp)
            err_print(
                f"sd {hexlify(ent)}\n   {hexlify(der.master_seed)}")
            assert der.master_seed == ent
            if mnem is not None:
                # assert der.master_seed == gen_ent
                mnem_words = der.electrum_words
                assert mnem_words.split(' ') == mnem.split(' ')
        # assert 1 == 2


if __name__ == '__main__':
    unittest.main()
