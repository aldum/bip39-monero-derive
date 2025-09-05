import unittest

from bip39 import wordlist
# from util import err_print


class TestUtils(unittest.TestCase):
    def test_wordlist(self):
        pl = wordlist.unique_prefix_length
        # for i in range(5):
        for i in range(wordlist.WORDS_LIST_NUM):
            word = wordlist[i]
            pref = word[:pl]
            # err_print(f"{pref} {wordlist[i]}")
            assert wordlist.unique_prefixes[pref] == word
        # assert 1 == 2


if __name__ == "__main__":
    unittest.main()
