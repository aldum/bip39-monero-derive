from typing import (
    Any,
    Optional,
    Dict,
    List,
)
from functools import reduce

class Singleton(type):
    # TODO proper self type
    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Wordlist:
    wordlist: List[str] = []
    WORDS_LIST_NUM: int = 0
    MAX_WORDLEN = 0
    m_words_to_idx: Dict[str, int] = {}
    unique_prefix_length: int = 0
    unique_prefixes: Dict[str, str] = {}

    def __init__(self):
        n = len(self.wordlist)
        self.WORDS_LIST_NUM = n
        self.MAX_WORDLEN = reduce(
            lambda a, s: max(a, len(s)), self.wordlist, 0)
        self.m_words_to_idx = {
            self.wordlist[i]: i for i in range(n)}
        self.unique_prefixes = {
            self.wordlist[i][:self.unique_prefix_length]:
                self.wordlist[i] for i in range(n)
        }

    def __getitem__(self, key):
        return self.wordlist[key]

    def get_word_idx_option(self, word: str) -> Optional[int]:
        try:
            return self.m_words_to_idx[word]
        except KeyError:
            return None

    def get_word_idx_unsafe(self, word: str) -> int:
        return self.get_word_idx_option(word) or self.MAX_WORDLEN + 1

    def contains(self, word: str) -> bool:
        return self.get_word_idx_option(word) is not None
