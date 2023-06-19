import re
import hmac
from hashlib import sha512
from binascii import hexlify, unhexlify

from ecdsa import SECP256k1, SigningKey # type: ignore
from ecdsa.ellipticcurve import Point # type: ignore


from util import memoize, IntegerUtils, hash160
from slip0010 import ed25519 as crypto

long_or_int = int
INFINITY = Point(None, None, None)


def ensure_bytes(data):
    if not isinstance(data, bytes):
        return data.encode("utf-8")
    return data


def ensure_str(data):
    if isinstance(data, bytes):
        return data.decode("utf-8")
    elif not isinstance(data, str):
        raise ValueError("Invalid value for string")
    return data


def is_hex_string(string):
    """Check if the string is only composed of hex characters."""
    pattern = re.compile(r"[A-Fa-f0-9]+")
    if isinstance(string, bytes):
        string = str(string)
    return pattern.match(string) is not None


def long_to_hex(ln, size):
    """Encode a long value as a hex string, 0-padding to size.
    Note that size is the size of the resulting hex string. So, for a 32Byte
    long size should be 64 (two hex characters per byte"."""
    f_str = "{0:0%sx}" % size
    # f_str = f"{0:0{size}x}"
    return ensure_bytes(f_str.format(ln).lower())


class Wallet:
    def __init__(
        self,
        chain_code,
        depth=0,
        parent_fingerprint=0,
        child_number=0,
        private_exponent=None,
        private_key=None,
        public_pair=None,
        public_key=None,
        # network="bitcoin_testnet",
        seed_secret=None,
        use_ed25519=False,
        use_slip0010=False,
    ):
        """Construct a new BIP32 compliant wallet.
        You probably don't want to use this init methd. Instead use one
        of the 'from_master_secret' or 'deserialize' cosntructors.
        """

        if not (private_exponent or private_key) and (
            not use_ed25519 and not (public_pair or public_key)
        ):
            raise InsufficientKeyDataError(
                "You must supply one of private_exponent or public_pair"
            )

        # network = Wallet.get_network(network)
        self.private_key = None
        self.public_key = None
        self.seed_secret = seed_secret
        self.use_ed25519 = use_ed25519
        self.use_slip0010 = use_slip0010
        if use_slip0010:
            raise NotImplementedError()

        if private_key:
            # if not isinstance(private_key, PrivateKey):
            if not isinstance(private_key, PrivateKey):
                raise InvalidPrivateKeyError(
                    "private_key must be of type bitmerchant.wallet.keys.PrivateKey"
                )
            self.private_key = private_key
        elif private_exponent:
            # self.private_key = PrivateKey(private_exponent, network=network)
            self.private_key = PrivateKey(private_exponent)

        if use_ed25519 and public_key:
            self.public_key = public_key
        elif use_ed25519:
            self.public_key = self.private_key.get_public_key()
        elif public_key:
            if not isinstance(public_key, PublicKey):
                raise InvalidPublicKeyError(
                    "public_key must be of type bitmerchant.wallet.keys.PublicKey"
                )
            self.public_key = public_key
        # elif public_pair:
        #     self.public_key = PublicKey.from_public_pair(
        #         public_pair,
        #         #  network=network
        #     )
        else:
            self.public_key = self.private_key.get_public_key()

        if (
            not self.use_ed25519
            and self.private_key
            and self.private_key.get_public_key() != self.public_key
        ):
            raise KeyMismatchError(
                "Provided private and public values do not match")

        def h(val, hex_len):
            if isinstance(val, int):
                return long_to_hex(val, hex_len)
            if isinstance(val, (str, bytes)) and is_hex_string(val):
                val = ensure_bytes(val)
                if len(val) != hex_len:
                    raise ValueError("Invalid parameter length")
                return val
            raise ValueError("Invalid parameter type")

        def l(val) -> int: # noqa: E743
            if isinstance(val, int):
                return long_or_int(val)
            if isinstance(val, (str, bytes)):
                val = ensure_bytes(val)
                if not is_hex_string(val):
                    val = hexlify(val)
                return long_or_int(val, 16)
            raise ValueError("parameter must be an int or long")

        # self.network = Wallet.get_network(network)
        self.depth = l(depth)
        if isinstance(parent_fingerprint, (str, bytes)):
            val = ensure_bytes(parent_fingerprint)
            if val.startswith(b"0x"):
                parent_fingerprint = val[2:]
        self.parent_fingerprint = b"0x" + h(parent_fingerprint, 8)
        self.child_number = l(child_number)
        self.chain_code = h(chain_code, 64)

    @ classmethod
    def from_master_secret(
        cls, seed, use_ed25519=False, use_slip0010=False
    ):
        """Generate a new PrivateKey from a secret key.
        :param seed: The key to use to generate this wallet. It may be a long
            string. Do not use a phrase from a book or song, as that will
            be guessed and is not secure. My advice is to not supply this
            argument and let me generate a new random key for you.
        :param network:
        :param use_ed25519:
        :param use_slip0010:
        See https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#Serialization_format
        See https://github.com/satoshilabs/slips/blob/master/slip-0010.md
        """
        seed = ensure_bytes(seed)
        # Given a seed S of at least 128 bits, but 256 is advised
        # Calculate I = HMAC-SHA512(key="Bitcoin seed", msg=S)
        cv_seed = b"Bitcoin seed"
        if use_ed25519:
            cv_seed = b"ed25519 seed"

        I = hmac.new(cv_seed, msg=seed, digestmod=sha512).digest() # noqa: E741
        # Split I into two 32-byte sequences, IL and IR.
        I_L, I_R = I[:32], I[32:]
        # Use IL as master secret key, and IR as master chain code.
        return cls(
            private_exponent=long_or_int(hexlify(I_L), 16),
            chain_code=long_or_int(hexlify(I_R), 16),
            seed_secret=seed,
            use_ed25519=use_ed25519,
            use_slip0010=use_slip0010,
        )

    def get_child_for_path(self, path):
        """Get a child for a given path.
        Rather than repeated calls to get_child, children can be found
        by a derivation path. Paths look like:
            m/0/1'/10
        Which is the same as
            self.get_child(0).get_child(-1).get_child(10)
        Or, in other words, the 10th publicly derived child of the 1st
        privately derived child of the 0th publicly derived child of master.
        You can use either ' or p to denote a prime (that is, privately
        derived) child.
        A child that has had its private key stripped can be requested by
        either passing a capital M or appending '.pub' to the end of the path.
        These three paths all give the same child that has had its private
        key scrubbed:
            M/0/1
            m/0/1.pub
            M/0/1.pub
        """
        path = ensure_str(path)

        if not path:
            raise InvalidPathError(f"{path} is not a valid path")

        # Figure out public/private derivation
        as_private = True
        if path.startswith("M"):
            as_private = False
        if path.endswith(".pub"):
            as_private = False
            path = path[:-4]

        parts = path.split("/")
        if len(parts) == 0:
            raise InvalidPathError()

        child = self
        for part in parts:
            if part.lower() == "m":
                continue
            is_prime = None  # Let primeness be figured out by the child number
            if part[-1] in "'p":
                is_prime = True
                part = part.replace("'", "").replace("p", "")
            try:
                child_number = long_or_int(part)
            except ValueError as e:
                raise InvalidPathError(f"{path} is not a valid path") from e
            child = child.get_child(child_number, is_prime)
        if not as_private:
            return child.public_copy()
        return child

    @ property
    def identifier(self):
        """Get the identifier for this node.
        Extended keys can be identified by the Hash160 (RIPEMD160 after SHA256)
        of the public key's `key`. This corresponds exactly to the data used in
        traditional Bitcoin addresses. It is not advised to represent this data
        in base58 format though, as it may be interpreted as an address that
        way (and wallet software is not required to accept payment to the chain
        key itself).
        """
        key = self.get_public_key_hex()
        return ensure_bytes(hexlify(hash160(unhexlify(key))))

    @ property
    def fingerprint(self):
        """The first 32 bits of the identifier are called the fingerprint."""
        # 32 bits == 4 Bytes == 8 hex characters
        return b"0x" + self.identifier[:8]

    @ memoize
    def get_child(self, child_number, is_prime=None, as_private=True):
        """Derive a child key.
        :param child_number: The number of the child key to compute
        :type child_number: int
        :param is_prime: If True, the child is calculated via private
            derivation. If False, then public derivation is used. If None,
            then it is figured out from the value of child_number.
        :type is_prime: bool, defaults to None
        :param as_private: If True, strips private key from the result.
            Defaults to False. If there is no private key present, this is
            ignored.
        :type as_private: bool
        Positive child_numbers (less than 2,147,483,648) produce publicly
        derived children.
        Negative numbers (greater than -2,147,483,648) uses private derivation.
        NOTE: Python can't do -0, so if you want the privately derived 0th
        child you need to manually set is_prime=True.
        NOTE: negative numbered children are provided as a convenience
        because nobody wants to remember the above numbers. Negative numbers
        are considered 'prime children', which is described in the BIP32 spec
        as a leading 1 in a 32 bit unsigned int.
        This derivation is fully described at
        https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#child-key-derivation-functions
        """
        boundary = 0x80000000

        if abs(child_number) >= boundary:
            raise ValueError(f"Invalid child number {child_number}")

        # If is_prime isn't set, then we can infer it from the child_number
        if is_prime is None:
            # Prime children are either < 0 or > 0x80000000
            if child_number < 0:
                child_number = abs(child_number)
                is_prime = True
            elif child_number >= boundary:
                child_number -= boundary
                is_prime = True
            else:
                is_prime = False
        else:
            # Otherwise is_prime is set so the child_number should be between
            # 0 and 0x80000000
            if child_number < 0 or child_number >= boundary:
                raise ValueError(
                    "Invalid child number. Must be between 0 and {boundary}"
                )

        if not self.private_key and is_prime:
            raise ValueError(
                "Cannot compute a prime child without a private key")

        if is_prime:
            # Even though we take child_number as an int < boundary, the
            # internal derivation needs it to be the larger number.
            child_number = child_number + boundary
        child_number_hex = long_to_hex(child_number, 8)
        # child_number_hex = hexlify(IntegerUtils.to_bytes(child_number))
        # err_print(f"cnh {child_number_hex}")

        if is_prime:
            # Let data = concat(0x00, self.key, child_number)
            data = b"00" + self.private_key.get_key()
        else:
            data = self.get_public_key_hex()
            if self.use_ed25519:
                raise InvalidPathError(
                    "Ed25519 public derivation is not implemented")

        data += child_number_hex

        # Compute a 64 Byte I that is the HMAC-SHA512, using self.chain_code
        # as the seed, and data as the message.
        # err_print(f"data: {data}")
        I = hmac.new( # noqa: E741
            unhexlify(self.chain_code),
            msg=unhexlify(data),
            digestmod=sha512
        ).digest()
        # Split I into its 32 Byte components.
        I_L, I_R = I[:32], I[32:]
        # if not self.use_ed25519 and long_or_int(hexlify(I_L), 16) >= SECP256k1.order:
        #     raise InvalidPrivateKeyError("The derived key is too large.")

        c_i = hexlify(I_R)
        private_exponent = None
        private_key = None
        public_key = None

        if self.use_ed25519 and not self.private_key:
            raise InvalidPathError(
                "Ed25519 public derivation is not implemented")

        if self.use_ed25519:
            private_key = Ed25519PrivateKey.from_hex_key(I_L)
            public_key = private_key.get_public_key()

        elif not self.use_ed25519 and self.private_key:
            # Use private information for derivation
            # I_L is added to the current key's secret exponent (mod n), where
            # n is the order of the ECDSA curve in use.
            private_exponent = (
                long_or_int(hexlify(I_L), 16)
                + long_or_int(self.private_key.get_key(), 16)
            ) % SECP256k1.order
            # I_R is the child's chain code
            private_key = PrivateKey(private_exponent)
            public_key = private_key.get_public_key()

        # elif not self.use_ed25519:
        #     # Only use public information for this derivation
        #     g = SECP256k1.generator
        #     I_L_long = long_or_int(hexlify(I_L), 16)
        #     point = (
        #         _ECDSA_Public_key(g, g * I_L_long).point +
        #         self.public_key.to_point()
        #     )
        #     # I_R is the child's chain code
        #     private_key = PrivateKey(private_exponent)
        #     public_key = PublicKey.from_public_pair(
        #         PublicPair(point.x(), point.y()))

        if public_key.to_point() == INFINITY:
            raise InfinityPointException("The point at infinity is invalid.")

        child = self.__class__(
            chain_code=c_i,
            depth=self.depth + 1,  # we have to go deeper...
            parent_fingerprint=self.fingerprint,
            child_number=child_number_hex,
            private_key=private_key,
            public_key=public_key,
            # network=self.network,
            use_slip0010=self.use_slip0010,
            use_ed25519=self.use_ed25519,
        )

        if not as_private:
            return child.public_copy()
        return child

    def public_copy(self):
        """Clone this wallet and strip it of its private information."""
        return self.__class__(
            chain_code=self.chain_code,
            depth=self.depth,
            parent_fingerprint=self.parent_fingerprint,
            child_number=self.child_number,
            public_pair=self.public_key.to_public_pair(),
            # network=self.network,
        )

    def get_public_key_hex(self, compressed=True):
        """Get the sec1 representation of the public key."""
        return ensure_bytes(self.public_key.get_key(compressed))


class InvalidPathError(Exception):
    pass


class InsufficientKeyDataError(ValueError):
    pass


class InvalidPrivateKeyError(ValueError):
    pass


class InvalidPublicKeyError(ValueError):
    pass


class KeyMismatchError(ValueError):
    pass


class InfinityPointException(Exception):
    pass


class Key():
    def __init__(self, compressed=False):
        """Construct a Key."""
        # Set network first because set_key needs it
        self.compressed = compressed

    def __eq__(self, other):
        return other and isinstance(self, type(other))

    def __ne__(self, other):
        return not self == other

    __hash__ = object.__hash__

    def get_key(self):
        raise NotImplementedError()


class PrivateKey(Key):
    def __init__(self, secret_exponent, *args, **kwargs):
        if not isinstance(secret_exponent, int):
            raise ValueError("secret_exponent must be a long")
        super().__init__(*args, **kwargs)
        self._private_key = SigningKey.from_secret_exponent(
            secret_exponent, curve=SECP256k1
        )

    def get_key(self):
        """Get the key - a hex formatted private exponent for the curve."""
        return ensure_bytes(hexlify(self._private_key.to_string()))

    @ memoize
    def get_public_key(self):
        """Get the PublicKey for this PrivateKey."""
        return PublicKey.from_verifying_key(
            self._private_key.get_verifying_key(),
            # network=self.network,
            compressed=self.compressed,
        )


class Ed25519PrivateKey(PrivateKey):
    def __init__(self, secret_exponent=None, key=None, hex_key=None):
        self._hex_key = hex_key
        self._key = None
        if secret_exponent:
            self._key = crypto.EdScalar(secret_exponent)
            # self._key = crypto.decodeint(
            #     bytes(crypto.EdScalar(secret_exponent)))
        elif hex_key:
            self._key = crypto.EdScalar(hex_key)
        else:
            self._key = crypto.EdScalar(key)
            # key

    def get_key(self) -> bytes:
        if self._hex_key:
            return ensure_bytes(hexlify(self._hex_key))
        # return ensure_bytes(hexlify(crypto.encodeint(self._key)))
        return IntegerUtils.to_bytes(self._key.v)

    def get_public_key(self):
        return Ed25519PublicKey(crypto.scalarmult_base(self._key))

    @ classmethod
    def from_hex_key(cls, key):
        return cls(hex_key=key)


class PublicKey(Key):
    def __init__(self, verifying_key, *args, **kwargs):
        """Create a public key.
        :param verifying_key: The ECDSA VerifyingKey corresponding to this
            public key.
        :type verifying_key: ecdsa.VerifyingKey
        :param network: The network you want (Networks just define certain
            constants, like byte-prefixes on public addresses).
        :type network: See `bitmerchant.wallet.network`
        """
        super(PublicKey, self).__init__(*args, **kwargs)
        self._verifying_key = verifying_key
        self.x = verifying_key.pubkey.point.x()
        self.y = verifying_key.pubkey.point.y()

    def get_key(self, compressed=None):
        """Get the hex-encoded key.
        :param compressed: False if you want a standard 65 Byte key (the most
            standard option). True if you want the compressed 33 Byte form.
            Defaults to None, which in turn uses the self.compressed attribute.
        :type compressed: bool
        PublicKeys consist of an ID byte, the x, and the y coordinates
        on the elliptic curve.
        In the case of uncompressed keys, the ID byte is 04.
        Compressed keys use the SEC1 format:
            If Y is odd: id_byte = 03
            else: id_byte = 02
        Note that I pieced this algorithm together from the pycoin source.
        This is documented in http://www.secg.org/collateral/sec1_final.pdf
        but, honestly, it's pretty confusing.
        I guess this is a pretty big warning that I'm not *positive* this
        will do the right thing in all cases. The tests pass, and this does
        exactly what pycoin does, but I'm not positive pycoin works either!
        """
        if compressed is None:
            compressed = self.compressed
        if compressed:
            parity = 2 + (self.y & 1)  # 0x02 even, 0x03 odd
            return ensure_bytes(long_to_hex(parity, 2) + long_to_hex(self.x, 64))
        else:
            return ensure_bytes(
                b"04" + long_to_hex(self.x, 64) + long_to_hex(self.y, 64)
            )

    @ classmethod
    def from_verifying_key(cls, verifying_key, **kwargs):
        return cls(verifying_key, **kwargs)


class Ed25519PublicKey(PublicKey):
    def __init__(self, key=None, *args, **kwargs):
        self._key = key

    def get_key(self, compressed=None):
        return ensure_bytes(hexlify(crypto.encodepoint(self._key)))

    @ classmethod
    def from_hex_key(cls, key):
        return cls(crypto.decodepoint(key))

    def to_point(self):
        return self

    def __eq__(self, other):
        if other == INFINITY:
            return crypto.point_eq(self._key, crypto.identity())
        return crypto.point_eq(self._key, other._key)
