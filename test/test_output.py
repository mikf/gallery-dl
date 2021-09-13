#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import output  # noqa E402


class TestShorten(unittest.TestCase):

    def test_shorten_noop(self, f=output.shorten_string):
        self.assertEqual(f(""      , 10), "")
        self.assertEqual(f("foobar", 10), "foobar")

    def test_shorten(self, f=output.shorten_string):
        s = "01234567890123456789"  # string of length 20
        self.assertEqual(f(s, 30), s)
        self.assertEqual(f(s, 25), s)
        self.assertEqual(f(s, 20), s)
        self.assertEqual(f(s, 19), "012345678…123456789")
        self.assertEqual(f(s, 18), "01234567…123456789")
        self.assertEqual(f(s, 17), "01234567…23456789")
        self.assertEqual(f(s, 16), "0123456…23456789")
        self.assertEqual(f(s, 15), "0123456…3456789")
        self.assertEqual(f(s, 14), "012345…3456789")
        self.assertEqual(f(s, 13), "012345…456789")
        self.assertEqual(f(s, 12), "01234…456789")
        self.assertEqual(f(s, 11), "01234…56789")
        self.assertEqual(f(s, 10), "0123…56789")
        self.assertEqual(f(s, 9) , "0123…6789")
        self.assertEqual(f(s, 3) , "0…9")
        self.assertEqual(f(s, 2) , "…9")

    def test_shorten_separator(self, f=output.shorten_string):
        s = "01234567890123456789"  # string of length 20
        self.assertEqual(f(s, 20, "|---|"), s)
        self.assertEqual(f(s, 19, "|---|"), "0123456|---|3456789")
        self.assertEqual(f(s, 15, "|---|"), "01234|---|56789")
        self.assertEqual(f(s, 10, "|---|"), "01|---|789")

        self.assertEqual(f(s, 19, "..."), "01234567...23456789")
        self.assertEqual(f(s, 19, "..") , "01234567..123456789")
        self.assertEqual(f(s, 19, ".")  , "012345678.123456789")
        self.assertEqual(f(s, 19, "")   , "0123456780123456789")


class TestShortenEAW(unittest.TestCase):

    def test_shorten_eaw_noop(self, f=output.shorten_string_eaw):
        self.assertEqual(f(""      , 10), "")
        self.assertEqual(f("foobar", 10), "foobar")

    def test_shorten_eaw(self, f=output.shorten_string_eaw):
        s = "01234567890123456789"  # 20 ascii characters
        self.assertEqual(f(s, 30), s)
        self.assertEqual(f(s, 25), s)
        self.assertEqual(f(s, 20), s)
        self.assertEqual(f(s, 19), "012345678…123456789")
        self.assertEqual(f(s, 18), "01234567…123456789")
        self.assertEqual(f(s, 17), "01234567…23456789")
        self.assertEqual(f(s, 16), "0123456…23456789")
        self.assertEqual(f(s, 15), "0123456…3456789")
        self.assertEqual(f(s, 14), "012345…3456789")
        self.assertEqual(f(s, 13), "012345…456789")
        self.assertEqual(f(s, 12), "01234…456789")
        self.assertEqual(f(s, 11), "01234…56789")
        self.assertEqual(f(s, 10), "0123…56789")
        self.assertEqual(f(s, 9) , "0123…6789")
        self.assertEqual(f(s, 3) , "0…9")
        self.assertEqual(f(s, 2) , "…9")

    def test_shorten_eaw_wide(self, f=output.shorten_string_eaw):
        s = "幻想郷幻想郷幻想郷幻想郷"  # 12 wide characters
        self.assertEqual(f(s, 30), s)
        self.assertEqual(f(s, 25), s)
        self.assertEqual(f(s, 20), "幻想郷幻…想郷幻想郷")
        self.assertEqual(f(s, 19), "幻想郷幻…想郷幻想郷")
        self.assertEqual(f(s, 18), "幻想郷幻…郷幻想郷")
        self.assertEqual(f(s, 17), "幻想郷幻…郷幻想郷")
        self.assertEqual(f(s, 16), "幻想郷…郷幻想郷")
        self.assertEqual(f(s, 15), "幻想郷…郷幻想郷")
        self.assertEqual(f(s, 14), "幻想郷…幻想郷")
        self.assertEqual(f(s, 13), "幻想郷…幻想郷")
        self.assertEqual(f(s, 12), "幻想…幻想郷")
        self.assertEqual(f(s, 11), "幻想…幻想郷")
        self.assertEqual(f(s, 10), "幻想…想郷")
        self.assertEqual(f(s, 9) , "幻想…想郷")
        self.assertEqual(f(s, 3) , "…郷")

    def test_shorten_eaw_mix(self, f=output.shorten_string_eaw):
        s = "幻-想-郷##幻-想-郷##幻-想-郷"  # mixed characters
        self.assertEqual(f(s, 28), s)
        self.assertEqual(f(s, 25), "幻-想-郷##幻…郷##幻-想-郷")

        self.assertEqual(f(s, 20), "幻-想-郷#…##幻-想-郷")
        self.assertEqual(f(s, 19), "幻-想-郷#…#幻-想-郷")
        self.assertEqual(f(s, 18), "幻-想-郷…#幻-想-郷")
        self.assertEqual(f(s, 17), "幻-想-郷…幻-想-郷")
        self.assertEqual(f(s, 16), "幻-想-…#幻-想-郷")
        self.assertEqual(f(s, 15), "幻-想-…幻-想-郷")
        self.assertEqual(f(s, 14), "幻-想-…-想-郷")
        self.assertEqual(f(s, 13), "幻-想-…-想-郷")
        self.assertEqual(f(s, 12), "幻-想…-想-郷")
        self.assertEqual(f(s, 11), "幻-想…想-郷")
        self.assertEqual(f(s, 10), "幻-…-想-郷")
        self.assertEqual(f(s, 9) , "幻-…想-郷")
        self.assertEqual(f(s, 3) , "…郷")

    def test_shorten_eaw_separator(self, f=output.shorten_string_eaw):
        s = "01234567890123456789"  # 20 ascii characters
        self.assertEqual(f(s, 20, "|---|"), s)
        self.assertEqual(f(s, 19, "|---|"), "0123456|---|3456789")
        self.assertEqual(f(s, 15, "|---|"), "01234|---|56789")
        self.assertEqual(f(s, 10, "|---|"), "01|---|789")

        self.assertEqual(f(s, 19, "..."), "01234567...23456789")
        self.assertEqual(f(s, 19, "..") , "01234567..123456789")
        self.assertEqual(f(s, 19, ".")  , "012345678.123456789")
        self.assertEqual(f(s, 19, "")   , "0123456780123456789")

    def test_shorten_eaw_separator_wide(self, f=output.shorten_string_eaw):
        s = "幻想郷幻想郷幻想郷幻想郷"  # 12 wide characters
        self.assertEqual(f(s, 24, "|---|"), s)
        self.assertEqual(f(s, 19, "|---|"), "幻想郷|---|郷幻想郷")
        self.assertEqual(f(s, 15, "|---|"), "幻想|---|幻想郷")
        self.assertEqual(f(s, 10, "|---|"), "幻|---|郷")

        self.assertEqual(f(s, 19, "..."), "幻想郷幻...郷幻想郷")
        self.assertEqual(f(s, 19, "..") , "幻想郷幻..郷幻想郷")
        self.assertEqual(f(s, 19, ".")  , "幻想郷幻.想郷幻想郷")
        self.assertEqual(f(s, 19, "")   , "幻想郷幻想郷幻想郷")

    def test_shorten_eaw_separator_mix_(self, f=output.shorten_string_eaw):
        s = "幻-想-郷##幻-想-郷##幻-想-郷"  # mixed characters
        self.assertEqual(f(s, 30, "|---|"), s)
        self.assertEqual(f(s, 19, "|---|"), "幻-想-|---|幻-想-郷")
        self.assertEqual(f(s, 15, "|---|"), "幻-想|---|想-郷")
        self.assertEqual(f(s, 10, "|---|"), "幻|---|-郷")

        self.assertEqual(f(s, 19, "..."), "幻-想-郷...幻-想-郷")
        self.assertEqual(f(s, 19, "..") , "幻-想-郷..#幻-想-郷")
        self.assertEqual(f(s, 19, ".")  , "幻-想-郷#.#幻-想-郷")
        self.assertEqual(f(s, 19, "")   , "幻-想-郷###幻-想-郷")


if __name__ == '__main__':
    unittest.main()
