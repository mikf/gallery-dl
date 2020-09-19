#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

import io
import random
import string
import http.cookiejar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import util, text, exception  # noqa E402


class TestRange(unittest.TestCase):

    def test_parse_range(self, f=util.RangePredicate.parse_range):
        self.assertEqual(
            f(""),
            [])
        self.assertEqual(
            f("1-2"),
            [(1, 2)])
        self.assertEqual(
            f("-"),
            [(1, sys.maxsize)])
        self.assertEqual(
            f("-2,4,6-8,10-"),
            [(1, 2), (4, 4), (6, 8), (10, sys.maxsize)])
        self.assertEqual(
            f(" - 3 , 4-  4, 2-6"),
            [(1, 3), (4, 4), (2, 6)])

    def test_optimize_range(self, f=util.RangePredicate.optimize_range):
        self.assertEqual(
            f([]),
            [])
        self.assertEqual(
            f([(2, 4)]),
            [(2, 4)])
        self.assertEqual(
            f([(2, 4), (6, 8), (10, 12)]),
            [(2, 4), (6, 8), (10, 12)])
        self.assertEqual(
            f([(2, 4), (4, 6), (5, 8)]),
            [(2, 8)])
        self.assertEqual(
            f([(1, 1), (2, 2), (3, 6), (8, 9)]),
            [(1, 6), (8, 9)])


class TestPredicate(unittest.TestCase):

    def test_range_predicate(self):
        dummy = None

        pred = util.RangePredicate(" - 3 , 4-  4, 2-6")
        for i in range(6):
            self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

        pred = util.RangePredicate("1, 3, 5")
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

        pred = util.RangePredicate("")
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

    def test_unique_predicate(self):
        dummy = None
        pred = util.UniquePredicate()

        # no duplicates
        self.assertTrue(pred("1", dummy))
        self.assertTrue(pred("2", dummy))
        self.assertFalse(pred("1", dummy))
        self.assertFalse(pred("2", dummy))
        self.assertTrue(pred("3", dummy))
        self.assertFalse(pred("3", dummy))

        # duplicates for "text:"
        self.assertTrue(pred("text:123", dummy))
        self.assertTrue(pred("text:123", dummy))
        self.assertTrue(pred("text:123", dummy))

    def test_filter_predicate(self):
        url = ""

        pred = util.FilterPredicate("a < 3")
        self.assertTrue(pred(url, {"a": 2}))
        self.assertFalse(pred(url, {"a": 3}))

        with self.assertRaises(SyntaxError):
            util.FilterPredicate("(")

        with self.assertRaises(exception.FilterError):
            util.FilterPredicate("a > 1")(url, {"a": None})

        with self.assertRaises(exception.FilterError):
            util.FilterPredicate("b > 1")(url, {"a": 2})

    def test_build_predicate(self):
        pred = util.build_predicate([])
        self.assertIsInstance(pred, type(lambda: True))

        pred = util.build_predicate([util.UniquePredicate()])
        self.assertIsInstance(pred, util.UniquePredicate)

        pred = util.build_predicate([util.UniquePredicate(),
                                     util.UniquePredicate()])
        self.assertIsInstance(pred, util.ChainPredicate)


class TestISO639_1(unittest.TestCase):

    def test_code_to_language(self):
        d = "default"
        self._run_test(util.code_to_language, {
            ("en",): "English",
            ("FR",): "French",
            ("xx",): None,
            (""  ,): None,
            (None,): None,
            ("en", d): "English",
            ("FR", d): "French",
            ("xx", d): d,
            (""  , d): d,
            (None, d): d,
        })

    def test_language_to_code(self):
        d = "default"
        self._run_test(util.language_to_code, {
            ("English",): "en",
            ("fRENch",): "fr",
            ("xx",): None,
            (""  ,): None,
            (None,): None,
            ("English", d): "en",
            ("fRENch", d): "fr",
            ("xx", d): d,
            (""  , d): d,
            (None, d): d,
        })

    def _run_test(self, func, tests):
        for args, result in tests.items():
            self.assertEqual(func(*args), result)


class TestCookiesTxt(unittest.TestCase):

    def test_load_cookiestxt(self):

        def _assert(content, expected):
            cookies = util.load_cookiestxt(io.StringIO(content, None))
            for c, e in zip(cookies, expected):
                self.assertEqual(c.__dict__, e.__dict__)

        _assert("", [])
        _assert("\n\n\n", [])
        _assert("$ Comment", [])
        _assert("# Comment", [])
        _assert(" # Comment \n\n $ Comment ", [])
        _assert(
            ".example.org\tTRUE\t/\tTRUE\t0\tname\tvalue",
            [self._cookie("name", "value", ".example.org")],
        )
        _assert(
            ".example.org\tTRUE\t/\tTRUE\t\tname\t",
            [self._cookie("name", "", ".example.org")],
        )
        _assert(
            "# Netscape HTTP Cookie File\n"
            "\n"
            "# default\n"
            ".example.org	TRUE	/	FALSE	0	n1	v1\n"
            ".example.org	TRUE	/	TRUE	2145945600	n2	v2\n"
            ".example.org	TRUE	/path	FALSE	0		n3\n"
            "\n"
            "  # # extra # #  \n"
            "www.example.org	FALSE	/	FALSE		n4	\n"
            "www.example.org	FALSE	/path	FALSE	100	n5	v5\n",
            [
                self._cookie(
                    "n1", "v1", ".example.org", True, "/", False),
                self._cookie(
                    "n2", "v2", ".example.org", True, "/", True, 2145945600),
                self._cookie(
                    "n3", None, ".example.org", True, "/path", False),
                self._cookie(
                    "n4", ""  , "www.example.org", False, "/", False),
                self._cookie(
                    "n5", "v5", "www.example.org", False, "/path", False, 100),
            ],
        )

        with self.assertRaises(ValueError):
            util.load_cookiestxt("example.org\tTRUE\t/\tTRUE\t0\tname")

    def test_save_cookiestxt(self):

        def _assert(cookies, expected):
            fp = io.StringIO(newline=None)
            util.save_cookiestxt(fp, cookies)
            self.assertMultiLineEqual(fp.getvalue(), expected)

        _assert([], "# Netscape HTTP Cookie File\n\n")
        _assert(
            [self._cookie("name", "value", ".example.org")],
            "# Netscape HTTP Cookie File\n\n"
            ".example.org\tTRUE\t/\tTRUE\t0\tname\tvalue\n",
        )
        _assert(
            [
                self._cookie(
                    "n1", "v1", ".example.org", True, "/", False),
                self._cookie(
                    "n2", "v2", ".example.org", True, "/", True, 2145945600),
                self._cookie(
                    "n3", None, ".example.org", True, "/path", False),
                self._cookie(
                    "n4", ""  , "www.example.org", False, "/", False),
                self._cookie(
                    "n5", "v5", "www.example.org", False, "/path", False, 100),
            ],
            "# Netscape HTTP Cookie File\n"
            "\n"
            ".example.org	TRUE	/	FALSE	0	n1	v1\n"
            ".example.org	TRUE	/	TRUE	2145945600	n2	v2\n"
            ".example.org	TRUE	/path	FALSE	0		n3\n"
            "www.example.org	FALSE	/	FALSE	0	n4	\n"
            "www.example.org	FALSE	/path	FALSE	100	n5	v5\n",
        )

    def _cookie(self, name, value, domain, domain_specified=True,
                path="/", secure=True, expires=None):
        return http.cookiejar.Cookie(
            0, name, value, None, False,
            domain, domain_specified, domain.startswith("."),
            path, False, secure, expires, False, None, None, {},
        )


class TestFormatter(unittest.TestCase):

    kwdict = {
        "a": "hElLo wOrLd",
        "b": "äöü",
        "d": {"a": "foo", "b": 0, "c": None},
        "l": ["a", "b", "c"],
        "n": None,
        "u": "%27%3C%20/%20%3E%27",
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
        self._run_test("{a!U}", self.kwdict["a"])
        self._run_test("{u!U}", "'< / >'")
        self._run_test("{a!s}", self.kwdict["a"])
        self._run_test("{a!r}", "'" + self.kwdict["a"] + "'")
        self._run_test("{a!a}", "'" + self.kwdict["a"] + "'")
        self._run_test("{b!a}", "'\\xe4\\xf6\\xfc'")
        self._run_test("{a!S}", self.kwdict["a"])
        self._run_test("{l!S}", "a, b, c")
        self._run_test("{n!S}", "")
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
        formatter = util.Formatter(format_string, default)
        output = formatter.format_map(self.kwdict)
        self.assertEqual(output, result, format_string)


class TestOther(unittest.TestCase):

    def test_bencode(self):
        self.assertEqual(util.bencode(0), "")
        self.assertEqual(util.bencode(123), "123")
        self.assertEqual(util.bencode(123, "01"), "1111011")
        self.assertEqual(util.bencode(123, "BA"), "AAAABAA")

    def test_bdecode(self):
        self.assertEqual(util.bdecode(""), 0)
        self.assertEqual(util.bdecode("123"), 123)
        self.assertEqual(util.bdecode("1111011", "01"), 123)
        self.assertEqual(util.bdecode("AAAABAA", "BA"), 123)

    def test_bencode_bdecode(self):
        for _ in range(100):
            value = random.randint(0, 1000000)
            for alphabet in ("01", "0123456789", string.ascii_letters):
                result = util.bdecode(util.bencode(value, alphabet), alphabet)
                self.assertEqual(result, value)

    def test_advance(self):
        items = range(5)

        self.assertCountEqual(
            util.advance(items, 0), items)
        self.assertCountEqual(
            util.advance(items, 3), range(3, 5))
        self.assertCountEqual(
            util.advance(items, 9), [])
        self.assertCountEqual(
            util.advance(util.advance(items, 1), 2), range(3, 5))

    def test_raises(self):
        func = util.raises(Exception)
        with self.assertRaises(Exception):
            func()

        func = util.raises(ValueError)
        with self.assertRaises(ValueError):
            func(1)
        with self.assertRaises(ValueError):
            func(2)
        with self.assertRaises(ValueError):
            func(3)

    def test_combine_dict(self):
        self.assertEqual(
            util.combine_dict({}, {}),
            {})
        self.assertEqual(
            util.combine_dict({1: 1, 2: 2}, {2: 4, 4: 8}),
            {1: 1, 2: 4, 4: 8})
        self.assertEqual(
            util.combine_dict(
                {1: {11: 22, 12: 24}, 2: {13: 26, 14: 28}},
                {1: {11: 33, 13: 39}, 2: "str"}),
            {1: {11: 33, 12: 24, 13: 39}, 2: "str"})
        self.assertEqual(
            util.combine_dict(
                {1: {2: {3: {4: {"1": "a", "2": "b"}}}}},
                {1: {2: {3: {4: {"1": "A", "3": "C"}}}}}),
            {1: {2: {3: {4: {"1": "A", "2": "b", "3": "C"}}}}})

    def test_transform_dict(self):
        d = {}
        util.transform_dict(d, str)
        self.assertEqual(d, {})

        d = {1: 123, 2: "123", 3: True, 4: None}
        util.transform_dict(d, str)
        self.assertEqual(
            d, {1: "123", 2: "123", 3: "True", 4: "None"})

        d = {1: 123, 2: "123", 3: "foo", 4: {11: 321, 12: "321", 13: "bar"}}
        util.transform_dict(d, text.parse_int)
        self.assertEqual(
            d, {1: 123, 2: 123, 3: 0, 4: {11: 321, 12: 321, 13: 0}})

    def test_filter_dict(self):
        d = {}
        r = util.filter_dict(d)
        self.assertEqual(r, d)
        self.assertIsNot(r, d)

        d = {"foo": 123, "bar": [], "baz": None}
        r = util.filter_dict(d)
        self.assertEqual(r, d)
        self.assertIsNot(r, d)

        d = {"foo": 123, "_bar": [], "__baz__": None}
        r = util.filter_dict(d)
        self.assertEqual(r, {"foo": 123})

    def test_number_to_string(self, f=util.number_to_string):
        self.assertEqual(f(1)     , "1")
        self.assertEqual(f(1.0)   , "1.0")
        self.assertEqual(f("1.0") , "1.0")
        self.assertEqual(f([1])   , [1])
        self.assertEqual(f({1: 2}), {1: 2})
        self.assertEqual(f(True)  , True)
        self.assertEqual(f(None)  , None)

    def test_to_string(self, f=util.to_string):
        self.assertEqual(f(1)    , "1")
        self.assertEqual(f(1.0)  , "1.0")
        self.assertEqual(f("1.0"), "1.0")

        self.assertEqual(f("")   , "")
        self.assertEqual(f(None) , "")
        self.assertEqual(f(0)    , "")

        self.assertEqual(f(["a"]), "a")
        self.assertEqual(f([1])  , "1")
        self.assertEqual(f(["a", "b", "c"]), "a, b, c")
        self.assertEqual(f([1, 2, 3]), "1, 2, 3")

    def test_universal_none(self):
        obj = util.NONE

        self.assertFalse(obj)
        self.assertEqual(str(obj), str(None))
        self.assertEqual(repr(obj), repr(None))
        self.assertIs(obj.attr, obj)
        self.assertIs(obj["key"], obj)


if __name__ == '__main__':
    unittest.main()
