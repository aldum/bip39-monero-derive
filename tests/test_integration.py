# pylint: disable=C0301
# import unittest
import unittest
from unittest import TestCase
from binascii import hexlify

from util import err_print
from tests.util import JSONUtils
from bip39 import mnemonics_to_ent  # , mnem_to_binstr
from slip0010 import sd


class TestUtils(TestCase):
    test_data = []

    def __init__(self, test_name):
        super().__init__(test_name)
        self.test_data = JSONUtils.load_vectors_from_file(
            'tests/test_vectors.json')

    def test_integration(self):
        for l in self.test_data:
            ent = l.seed
            ent = l.entropy
            gen_ent = mnemonics_to_ent(l.bip39, l.passp)
            mnem = l.monero_mnem
            # err_print(f"b58 {hexlify(gen_ent)}")
            assert ent == gen_ent
            if mnem is not None:
                der = sd.SeedDerivation.derive_monero(l.bip39, l.passp)
                assert der.master_seed == gen_ent
                asdf = der.monero_master
                err_print(f"mm {hexlify(asdf)}")
                mnem_words = der.electrum_words
                assert mnem_words.split(' ') == mnem.split(' ')
        # assert 1 == 2


if __name__ == '__main__':
    unittest.main()
