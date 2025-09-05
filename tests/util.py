import json
from typing import List, Optional
from binascii import unhexlify
from dataclasses import dataclass


@dataclass
class TestVector:
    seed: bytes
    bip39: str
    passp: str
    entropy: bytes
    monero_mnem: Optional[str]
    public_addr: Optional[str]


class JSONUtils:
    @staticmethod
    def load_json_file(filename: str) -> str:
        f = open(filename, encoding="utf-8")

        data = json.load(f)

        f.close()
        return data

    @staticmethod
    def load_vectors_data(data: str) -> List[TestVector]:
        def to_vect(line):
            monero_mnem = None
            public_addr = None
            if len(line) == 6:
                [seed, bip39, passp, ent, monero_mnem, public_addr] = line
            elif len(line) == 4:
                [seed, bip39, passp, ent] = line
            base_hex = unhexlify(seed)
            ent_b = unhexlify(ent)
            return TestVector(
                base_hex, bip39, passp, ent_b, monero_mnem, public_addr
            )

        return [to_vect(line) for line in data]

    @staticmethod
    def load_vectors_from_file(filename: str) -> List[TestVector]:
        data = JSONUtils.load_json_file(filename)
        return JSONUtils.load_vectors_data(data)
