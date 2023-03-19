# pylint: disable=C0301
# import unittest
import unittest
from unittest import TestCase
from binascii import hexlify, unhexlify

from util import JSONUtils, err_print, IntegerUtils
from bip39 import mnemonics_to_seed  # , mnem_to_binstr
from slip0010 import derive_monero_master_key
from monero_mnemonic import encode
from monero_mnemonic import encode_int


class TestUtils(TestCase):
    test_data = []
    # test_b = 'c9251180cf1053c02b4900dff7a3cd1d0821daeed048bc5c640e9b884d3137edc40e2c08919520214fb735d6762c971ea21b1dfd347f5a0be3ce1217bd133a7e'

    def __init__(self, test_name):
        super().__init__(test_name)
        self.test_data = JSONUtils.load_vectors_from_file(
            'tests/test_vectors.json')

    def test_integration(self):
        for l in self.test_data:
            seed = unhexlify(l.entropy)
            gen_seed = mnemonics_to_seed(l.bip39, l.passp)
            mnem = l.monero_mnem
            assert seed == gen_seed
            if mnem is not None:
                (monero_key, _) = derive_monero_master_key(gen_seed)
                # err_print(f"key {hexlify(IntegerUtils.to_bytes(monero_key))}")
                # err_print(f"il {hexlify(gen_seed)}")
                # [I_L, _] = _derive_monero_master_key(gen_seed)
                # assert int.from_bytes(I_L, "big") == int(hexlify(I_L), 16)
                # mnem_words = encode(I_L)
                # mnem_words = encode(monero_key)
                mnem_words = encode_int(monero_key)
                assert mnem_words == mnem.split(' ')
        # assert 1 == 2


if __name__ == '__main__':
    unittest.main()
