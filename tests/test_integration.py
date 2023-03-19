# pylint: disable=C0301
# import unittest
import unittest
from unittest import TestCase
from binascii import hexlify

from util import JSONUtils, err_print
from bip39 import mnemonics_to_ent  # , mnem_to_binstr
from slip0010 import sd
from monero_mnemonic import *


class TestUtils(TestCase):
    test_data = []
    # test_b = 'c9251180cf1053c02b4900dff7a3cd1d0821daeed048bc5c640e9b884d3137edc40e2c08919520214fb735d6762c971ea21b1dfd347f5a0be3ce1217bd133a7e'

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
