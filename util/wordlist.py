from typing import Optional
from functools import reduce


class Wordlist:
    wordlist = []
    WORDS_LIST_NUM: int = 0
    MAX_WORDLEN = 0
    m_words_to_idx = {}

    def __init__(self):
        self.WORDS_LIST_NUM = len(self.wordlist)
        self.MAX_WORDLEN = reduce(
            lambda a, s: max(a, len(s)), self.wordlist, 0)
        self.m_words_to_idx = {
            self.wordlist[i]: i for i in range(len(self.wordlist))}

    def __getitem__(self, key):
        return self.wordlist[key]

    def get_word_idx(self, word: str) -> Optional[int]:
        try:
            return self.m_words_to_idx[word]
        except KeyError:
            return None

    def contains(self, word: str) -> bool:
        return self.get_word_idx(word) is not None
