import binascii

import bip39
from slip0010.wallet import Wallet
from slip0010 import ed25519 as crypto
from monero_mnemonic import mn_encode

DEFAULT_BIP44_PATH = "m/44'/128'/0'/0/0"
DEFAULT_SLIP0010_PATH = "m/44'/128'/0'"


def _offset(x, offset=0):
    if offset == 0:
        return x
    return x[offset:]


def encodeint(x):
    return bytes(x)


def decodeint(x, offset=0):
    return crypto.EdScalar(_offset(x, offset))


class SeedDerivation(object):
    def __init__(self):
        self.mnemonics = None
        self.mnemonics_as_idx = False
        self.master_seed = None
        self.pre_hash = None
        self.monero_master = None
        self.electrum_words = None
        self.is_slip0010 = False
        self.path = None

        self.spend_sec = None
        self.spend_pub = None
        self.view_sec = None
        self.view_pub = None

    def set_seed(self, seed, path=None, slip0010=False):
        """
        Sets master secret for BIP44 derivation
        :param seed:
        :param path:
        :param slip0010:
        :return:
        """
        self.master_seed = seed
        self.is_slip0010 = slip0010
        if path is None:
            self.path = DEFAULT_BIP44_PATH if not slip0010 else DEFAULT_SLIP0010_PATH
        else:
            self.path = path
        wl = Wallet.from_master_secret(seed, use_ed25519=slip0010)

        # Generate private keys based on the gen mechanism. Bip44 path + Monero backward compatible
        data = wl.get_child_for_path(self.path)
        self.pre_hash = binascii.unhexlify(data.private_key.get_key())

        if slip0010:
            self.monero_master = encodeint(decodeint(self.pre_hash))
        else:
            # Ledger way = words -> bip39 pbkdf -> master seed -> bip32 normal with
            #  "Bitcoin seed" seed, get private key node -> cn_fast_hash -> monero master secret
            self.monero_master = crypto.cn_fast_hash(self.pre_hash)

        self.set_monero_seed(self.monero_master)

    def set_monero_seed(self, seed):
        """
        Sets Monero master secret seed.
        :param seed:
        :return:
        """
        # to_hash is initial seed in the Monero sense, recoverable from this seed
        self.monero_master = seed
        self.electrum_words = " ".join(
            # mnemonic.mn_encode(self.monero_master, True))
            mn_encode(self.monero_master, True))

        keys = crypto.generate_monero_keys(self.monero_master)
        self.spend_sec, self.spend_pub = keys  # , self.view_sec, self.view_pub = keys

    # def creds(self, network_type=NetworkTypes.MAINNET):
    #     return monero.AccountCreds.new_wallet(
    #         priv_view_key=self.view_sec,
    #         priv_spend_key=self.spend_sec,
    #         network_type=network_type,
    #     )

    @staticmethod
    def clean_input(inp):
        cleaned = []
        if isinstance(inp, (str, bytes)):
            cleaned = [inp]

        else:
            for w in inp:
                cleaned += w.split(" ")

        cleaned = [x.strip().lower() for x in cleaned]
        return cleaned

    @classmethod
    def from_mnemonics(cls, mnemonics, as_index=False, passphrase=b"", *args, **kwargs):
        mnems = SeedDerivation.clean_input(mnemonics)

        # if as_index:
        #     if passphrase:
        #         raise ValueError(
        #             "Passphrase not supported for index mnemonic interpretation")

        #     indices = [bip39.english_words.index(x) for x in mnems]
        #     seed = bip32.Wallet.indices_to_bytes(indices)

        # else:
        seed = bip39.mnemonics_to_seed(mnemonics, passphrase=passphrase)

        r = cls()
        r.mnemonics = mnems
        r.mnemonics_as_idx = as_index
        r.set_seed(seed, *args, **kwargs)
        return r

    @classmethod
    def from_master_seed(cls, seed, *args, **kwargs):
        r = cls()
        r.set_seed(seed, *args, **kwargs)
        return r

    @classmethod
    def from_monero_seed(cls, seed):
        r = cls()
        r.set_monero_seed(seed)
        return r

    # @classmethod
    # def from_monero_mnemonics(cls, mnemonics_words, *args, **kwargs):
    #     mnems = SeedDerivation.clean_input(mnemonics_words)
    #     seed = mnemonic.mn_decode(mnems)

    #     r = cls()
    #     r.set_monero_seed(binascii.unhexlify(seed))
    #     return r

    @classmethod
    def derive_monero(cls, mnem, passp):
        deriv_args = {}
        deriv_args["slip0010"] = True
        return SeedDerivation.from_mnemonics(
            mnem, passphrase=passp.encode("utf8"), **deriv_args)
