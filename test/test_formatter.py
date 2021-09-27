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
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import formatter  # noqa E402


class TestFormatter(unittest.TestCase):

    kwdict = {
        "a": "hElLo wOrLd",
        "b": "äöü",
        "d": {"a": "foo", "b": 0, "c": None},
        "l": ["a", "b", "c"],
        "n": None,
        "s": " \n\r\tSPACE    ",
        "u": "&#x27;&lt; / &gt;&#x27;",
        "t": 1262304000,
        "dt": datetime.datetime(2010, 1, 1),
        "name": "Name",
        "title1": "Title",
        "title2": "",
        "title3": None,
        "title4": 0,
    }

    def test_conversions(self):
        self._run_test("{a!l}", "hello world")
        self._run_test("{a!u}", "HELLO WORLD")
        self._run_test("{a!c}", "Hello world")
        self._run_test("{a!C}", "Hello World")
        self._run_test("{s!t}", "SPACE")
        self._run_test("{a!U}", self.kwdict["a"])
        self._run_test("{u!U}", "'< / >'")
        self._run_test("{a!s}", self.kwdict["a"])
        self._run_test("{a!r}", "'" + self.kwdict["a"] + "'")
        self._run_test("{a!a}", "'" + self.kwdict["a"] + "'")
        self._run_test("{b!a}", "'\\xe4\\xf6\\xfc'")
        self._run_test("{a!S}", self.kwdict["a"])
        self._run_test("{l!S}", "a, b, c")
        self._run_test("{n!S}", "")
        self._run_test("{t!d}", datetime.datetime(2010, 1, 1))
        self._run_test("{t!d:%Y-%m-%d}", "2010-01-01")
        self._run_test("{dt!T}", "1262304000")
        self._run_test("{l!j}", '["a", "b", "c"]')

        with self.assertRaises(KeyError):
            self._run_test("{a!q}", "hello world")

    def test_optional(self):
        self._run_test("{name}{title1}", "NameTitle")
        self._run_test("{name}{title1:?//}", "NameTitle")
        self._run_test("{name}{title1:? **/''/}", "Name **Title''")

        self._run_test("{name}{title2}", "Name")
        self._run_test("{name}{title2:?//}", "Name")
        self._run_test("{name}{title2:? **/''/}", "Name")

        self._run_test("{name}{title3}", "NameNone")
        self._run_test("{name}{title3:?//}", "Name")
        self._run_test("{name}{title3:? **/''/}", "Name")

        self._run_test("{name}{title4}", "Name0")
        self._run_test("{name}{title4:?//}", "Name")
        self._run_test("{name}{title4:? **/''/}", "Name")

    def test_missing(self):
        replacement = "None"

        self._run_test("{missing}", replacement)
        self._run_test("{missing.attr}", replacement)
        self._run_test("{missing[key]}", replacement)
        self._run_test("{missing:?a//}", "")

        self._run_test("{name[missing]}", replacement)
        self._run_test("{name[missing].attr}", replacement)
        self._run_test("{name[missing][key]}", replacement)
        self._run_test("{name[missing]:?a//}", "")

    def test_missing_custom_default(self):
        replacement = default = "foobar"
        self._run_test("{missing}"     , replacement, default)
        self._run_test("{missing.attr}", replacement, default)
        self._run_test("{missing[key]}", replacement, default)
        self._run_test("{missing:?a//}", "a" + default, default)

    def test_alternative(self):
        self._run_test("{a|z}"    , "hElLo wOrLd")
        self._run_test("{z|a}"    , "hElLo wOrLd")
        self._run_test("{z|y|a}"  , "hElLo wOrLd")
        self._run_test("{z|y|x|a}", "hElLo wOrLd")
        self._run_test("{z|n|a|y}", "hElLo wOrLd")

        self._run_test("{z|a!C}"      , "Hello World")
        self._run_test("{z|a:Rh/C/}"  , "CElLo wOrLd")
        self._run_test("{z|a!C:RH/C/}", "Cello World")
        self._run_test("{z|y|x:?</>/}", "")

        self._run_test("{d[c]|d[b]|d[a]}", "foo")
        self._run_test("{d[a]|d[b]|d[c]}", "foo")
        self._run_test("{d[z]|d[y]|d[x]}", "None")

    def test_indexing(self):
        self._run_test("{l[0]}" , "a")
        self._run_test("{a[6]}" , "w")

    def test_slicing(self):
        v = self.kwdict["a"]
        self._run_test("{a[1:10]}"  , v[1:10])
        self._run_test("{a[-10:-1]}", v[-10:-1])
        self._run_test("{a[5:]}" , v[5:])
        self._run_test("{a[50:]}", v[50:])
        self._run_test("{a[:5]}" , v[:5])
        self._run_test("{a[:50]}", v[:50])
        self._run_test("{a[:]}"  , v)
        self._run_test("{a[1:10:2]}"  , v[1:10:2])
        self._run_test("{a[-10:-1:2]}", v[-10:-1:2])
        self._run_test("{a[5::2]}" , v[5::2])
        self._run_test("{a[50::2]}", v[50::2])
        self._run_test("{a[:5:2]}" , v[:5:2])
        self._run_test("{a[:50:2]}", v[:50:2])
        self._run_test("{a[::]}"   , v)

    def test_maxlen(self):
        v = self.kwdict["a"]
        self._run_test("{a:L5/foo/}" , "foo")
        self._run_test("{a:L50/foo/}", v)
        self._run_test("{a:L50/foo/>50}", " " * 39 + v)
        self._run_test("{a:L50/foo/>51}", "foo")
        self._run_test("{a:Lab/foo/}", "foo")

    def test_join(self):
        self._run_test("{l:J}"       , "abc")
        self._run_test("{l:J,}"      , "a,b,c")
        self._run_test("{l:J,/}"     , "a,b,c")
        self._run_test("{l:J,/>20}"  , "               a,b,c")
        self._run_test("{l:J - }"    , "a - b - c")
        self._run_test("{l:J - /}"   , "a - b - c")
        self._run_test("{l:J - />20}", "           a - b - c")

        self._run_test("{a:J/}"      , self.kwdict["a"])
        self._run_test("{a:J, /}"    , ", ".join(self.kwdict["a"]))

    def test_replace(self):
        self._run_test("{a:Rh/C/}"  , "CElLo wOrLd")
        self._run_test("{a!l:Rh/C/}", "Cello world")
        self._run_test("{a!u:Rh/C/}", "HELLO WORLD")

        self._run_test("{a!l:Rl/_/}", "he__o wor_d")
        self._run_test("{a!l:Rl//}" , "heo word")
        self._run_test("{name:Rame/othing/}", "Nothing")

    def test_chain_special(self):
        # multiple replacements
        self._run_test("{a:Rh/C/RE/e/RL/l/}", "Cello wOrld")
        self._run_test("{d[b]!s:R1/Q/R2/A/R0/Y/}", "Y")

        # join-and-replace
        self._run_test("{l:J-/Rb/E/}", "a-E-c")

        # optional-and-maxlen
        self._run_test("{d[a]:?</>/L1/too long/}", "<too long>")
        self._run_test("{d[c]:?</>/L5/too long/}", "")

    def _run_test(self, format_string, result, default=None):
        fmt = formatter.parse(format_string, default)
        output = fmt.format_map(self.kwdict)
        self.assertEqual(output, result, format_string)


if __name__ == '__main__':
    unittest.main()
