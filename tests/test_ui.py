import os
import curses
import select
import pytest
import unittest
from typing import Any, Callable

from ui import program
import pyte  # type: ignore

uitest = pytest.mark.skipif(
    "not config.getoption('--run-curses-test')",
    reason="Only run when --run-curses-test is given",
)


@uitest
class TestUI(unittest.TestCase):
    @staticmethod
    def _test_wrapper(test: Callable[[Any], Any]) -> None:
        pid, f_d = os.forkpty()
        if pid == 0:
            curses.wrapper(program)
        else:
            test(f_d)

    def test_bounds_check(self):
        def test(f_d):
            # screen = pyte.Screen(10, 20)
            self.assertRaises(AssertionError)

        self._test_wrapper(test)

    def test_tui(self):
        def test(f_d) -> None:
            screen = pyte.Screen(80, 25)
            stream = pyte.ByteStream(screen)

            os.write(f_d, str.encode("\n"))
            for i in range(11):
                os.write(f_d, str.encode("aban\n"))
            os.write(f_d, str.encode("abou\n"))
            os.write(f_d, str.encode("j"))  # picker down
            os.write(f_d, str.encode("\n"))
            while True:
                try:
                    [f_d], _, _ = select.select([f_d], [], [], 1)
                except (KeyboardInterrupt, ValueError):
                    # either test was interrupted or the
                    # file descriptor of the child process
                    # provides nothing to be read
                    break
                else:
                    try:
                        # scrape screen of child process
                        data = os.read(f_d, 1024)
                        stream.feed(data)
                    except OSError:
                        # reading empty
                        break
            # for line in screen.display[11]:
            #     print(line)
            l1: str = screen.display[11]
            l2: str = screen.display[12]
            part1 = "alchemy apart fowls dexterity puck films liquid vigilant yesterday people awful"
            part2 = "blender plywood"
            self.assertEqual(l1.strip(), part1)
            self.assertEqual(l2.strip(), part2)
            # print(l1)
            # print(l2)
            # self.assertEqual(1, 2)

        self._test_wrapper(test)

    def test_tui2(self):
        def test(f_d) -> None:
            screen = pyte.Screen(80, 25)
            stream = pyte.ByteStream(screen)

            os.write(f_d, str.encode("\n"))
            for i in range(11):
                os.write(f_d, str.encode("add\n"))
            os.write(f_d, str.encode("actor\n"))
            os.write(f_d, str.encode("j"))  # picker down
            os.write(f_d, str.encode("\n"))
            while True:
                try:
                    [f_d], _, _ = select.select([f_d], [], [], 1)
                except (KeyboardInterrupt, ValueError):
                    # either test was interrupted or the
                    # file descriptor of the child process
                    # provides nothing to be read
                    break
                else:
                    try:
                        # scrape screen of child process
                        data = os.read(f_d, 1024)
                        stream.feed(data)
                    except OSError:
                        # reading empty
                        break
            # for line in screen.display:
            #     print(line)
            l1: str = screen.display[9]
            l2: str = screen.display[10]
            l3: str = screen.display[11]
            part1 = "rejoices dynamite faulty intended pelican fetches mighty baptism madness dwelt"
            part2 = "epoxy cactus vulture menu licks jaded leech subtly tell pebbles physics almost"
            part3 = "spout suitcase cactus"
            print(l1)
            print(l2)
            print(l3)
            self.assertEqual(l1.strip(), part1)
            self.assertEqual(l2.strip(), part2)
            self.assertEqual(l3.strip(), part3)
            # self.assertEqual(1, 2)

        self._test_wrapper(test)


if __name__ == "__main__":
    unittest.main()
