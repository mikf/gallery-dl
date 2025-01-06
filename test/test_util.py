#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

import io
import time
import random
import string
import datetime
import platform
import tempfile
import itertools
import http.cookiejar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import util, text, exception  # noqa E402


class TestRange(unittest.TestCase):

    def test_parse_empty(self, f=util.RangePredicate._parse):
        self.assertEqual(f(""), [])
        self.assertEqual(f([]), [])

    def test_parse_digit(self, f=util.RangePredicate._parse):
        self.assertEqual(f("2"), [range(2, 3)])

        self.assertEqual(
            f("2, 3, 4"),
            [range(2, 3),
             range(3, 4),
             range(4, 5)],
        )

    def test_parse_range(self, f=util.RangePredicate._parse):
        self.assertEqual(f("1-2"), [range(1, 3)])
        self.assertEqual(f("2-"), [range(2, sys.maxsize)])
        self.assertEqual(f("-3"), [range(1, 4)])
        self.assertEqual(f("-"), [range(1, sys.maxsize)])

        self.assertEqual(
            f("-2,4,6-8,10-"),
            [range(1, 3),
             range(4, 5),
             range(6, 9),
             range(10, sys.maxsize)],
        )
        self.assertEqual(
            f(" - 3 , 4-  4, 2-6"),
            [range(1, 4),
             range(4, 5),
             range(2, 7)],
        )

    def test_parse_slice(self, f=util.RangePredicate._parse):
        self.assertEqual(f("2:4")  , [range(2, 4)])
        self.assertEqual(f("3::")  , [range(3, sys.maxsize)])
        self.assertEqual(f(":4:")  , [range(1, 4)])
        self.assertEqual(f("::5")  , [range(1, sys.maxsize, 5)])
        self.assertEqual(f("::")   , [range(1, sys.maxsize)])
        self.assertEqual(f("2:3:4"), [range(2, 3, 4)])

        self.assertEqual(
            f("2:4, 4:, :4, :4:, ::4"),
            [range(2, 4),
             range(4, sys.maxsize),
             range(1, 4),
             range(1, 4),
             range(1, sys.maxsize, 4)],
        )
        self.assertEqual(
            f(" : 3 , 4:  4, 2:6"),
            [range(1, 3),
             range(4, 4),
             range(2, 6)],
        )


class TestPredicate(unittest.TestCase):

    def test_range_predicate(self):
        dummy = None

        pred = util.RangePredicate(" - 3 , 4-  4, 2-6")
        for i in range(6):
            self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            pred(dummy, dummy)

        pred = util.RangePredicate("1, 3, 5")
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            pred(dummy, dummy)

        pred = util.RangePredicate("")
        with self.assertRaises(exception.StopExtraction):
            pred(dummy, dummy)

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

        self.assertFalse(
            util.FilterPredicate("a > 1")(url, {"a": None}))
        self.assertFalse(
            util.FilterPredicate("b > 1")(url, {"a": 2}))

        pred = util.FilterPredicate(["a < 3", "b < 4", "c < 5"])
        self.assertTrue(pred(url, {"a": 2, "b": 3, "c": 4}))
        self.assertFalse(pred(url, {"a": 3, "b": 3, "c": 4}))
        self.assertFalse(pred(url, {"a": 2, "b": 4, "c": 4}))
        self.assertFalse(pred(url, {"a": 2, "b": 3, "c": 5}))

        self.assertFalse(pred(url, {"a": 2}))

    def test_build_predicate(self):
        pred = util.build_predicate([])
        self.assertIsInstance(pred, type(lambda: True))

        pred = util.build_predicate([util.UniquePredicate()])
        self.assertIsInstance(pred, util.UniquePredicate)

        pred = util.build_predicate([util.UniquePredicate(),
                                     util.UniquePredicate()])
        self.assertIs(pred.func, util.chain_predicates)


class TestISO639_1(unittest.TestCase):

    def test_code_to_language(self):
        d = "default"
        self._run_test(util.code_to_language, {
            ("en",): "English",
            ("FR",): "French",
            ("ja",): "Japanese",
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
            ("Japanese",): "ja",
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

    def test_cookiestxt_load(self):

        def _assert(content, expected):
            cookies = util.cookiestxt_load(io.StringIO(content, None))
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
            "\tTRUE\t/\tTRUE\t\tname\t",
            [self._cookie("name", "", "")],
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
            util.cookiestxt_load("example.org\tTRUE\t/\tTRUE\t0\tname")

    def test_cookiestxt_store(self):

        def _assert(cookies, expected):
            fp = io.StringIO(newline=None)
            util.cookiestxt_store(fp, cookies)
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
                self._cookie(
                    "n6", "v6", "", False),
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


class TestCompileExpression(unittest.TestCase):

    def test_compile_expression(self):
        expr = util.compile_expression("1 + 2 * 3")
        self.assertEqual(expr(), 7)
        self.assertEqual(expr({"a": 1, "b": 2, "c": 3}), 7)
        self.assertEqual(expr({"a": 9, "b": 9, "c": 9}), 7)

        expr = util.compile_expression("a + b * c")
        self.assertEqual(expr({"a": 1, "b": 2, "c": 3}), 7)
        self.assertEqual(expr({"a": 9, "b": 9, "c": 9}), 90)

        with self.assertRaises(SyntaxError):
            util.compile_expression("")
        with self.assertRaises(SyntaxError):
            util.compile_expression("x++")

        expr = util.compile_expression("1 and abort()")
        with self.assertRaises(exception.StopExtraction):
            expr()

    def test_compile_expression_raw(self):
        expr = util.compile_expression_raw("a + b * c")
        with self.assertRaises(NameError):
            expr()
        with self.assertRaises(NameError):
            expr({"a": 2})

        expr = util.compile_expression_raw("int.param")
        with self.assertRaises(AttributeError):
            expr({"a": 2})

    def test_compile_expression_tryexcept(self):
        expr = util.compile_expression_tryexcept("a + b * c")
        self.assertIs(expr(), util.NONE)
        self.assertIs(expr({"a": 2}), util.NONE)

        expr = util.compile_expression_tryexcept("int.param")
        self.assertIs(expr({"a": 2}), util.NONE)

    def test_compile_expression_defaultdict(self):
        expr = util.compile_expression_defaultdict("a + b * c")
        self.assertIs(expr(), util.NONE)
        self.assertIs(expr({"a": 2}), util.NONE)

        expr = util.compile_expression_defaultdict("int.param")
        with self.assertRaises(AttributeError):
            expr({"a": 2})

    def test_compile_filter(self):
        expr = util.compile_filter("a + b * c")
        self.assertEqual(expr({"a": 1, "b": 2, "c": 3}), 7)
        self.assertEqual(expr({"a": 9, "b": 9, "c": 9}), 90)

        expr = util.compile_filter(["a % 2 == 0", "b % 3 == 0", "c % 5 == 0"])
        self.assertTrue(expr({"a": 4, "b": 6, "c": 10}))
        self.assertFalse(expr({"a": 1, "b": 2, "c": 3}))

    def test_custom_globals(self):
        value = {"v": "foobar"}
        result = "8843d7f92416211de9ebb963ff4ce28125932878"

        expr = util.compile_expression("hash_sha1(v)")
        self.assertEqual(expr(value), result)

        expr = util.compile_expression("hs(v)", globals={"hs": util.sha1})
        self.assertEqual(expr(value), result)

        with tempfile.TemporaryDirectory() as path:
            file = path + "/module_sha1.py"
            with open(file, "w") as fp:
                fp.write("""
import hashlib
def hash(value):
    return hashlib.sha1(value.encode()).hexdigest()
""")
            module = util.import_file(file)

        expr = util.compile_expression("hash(v)", globals=module.__dict__)
        self.assertEqual(expr(value), result)

        GLOBALS_ORIG = util.GLOBALS
        try:
            util.GLOBALS = module.__dict__
            expr = util.compile_expression("hash(v)")
        finally:
            util.GLOBALS = GLOBALS_ORIG
        self.assertEqual(expr(value), result)


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

    def test_unique(self):
        self.assertSequenceEqual(
            list(util.unique("")), "")
        self.assertSequenceEqual(
            list(util.unique("AABBCC")), "ABC")
        self.assertSequenceEqual(
            list(util.unique("ABABABCAABBCC")), "ABC")
        self.assertSequenceEqual(
            list(util.unique([1, 2, 1, 3, 2, 1])), [1, 2, 3])

    def test_unique_sequence(self):
        self.assertSequenceEqual(
            list(util.unique_sequence("")), "")
        self.assertSequenceEqual(
            list(util.unique_sequence("AABBCC")), "ABC")
        self.assertSequenceEqual(
            list(util.unique_sequence("ABABABCAABBCC")), "ABABABCABC")
        self.assertSequenceEqual(
            list(util.unique_sequence([1, 2, 1, 3, 2, 1])), [1, 2, 1, 3, 2, 1])

    def test_contains(self):
        c = [1, "2", 3, 4, "5", "foo"]
        self.assertTrue(util.contains(c, 1))
        self.assertTrue(util.contains(c, "foo"))
        self.assertTrue(util.contains(c, [1, 3, "5"]))
        self.assertTrue(util.contains(c, ["a", "b", "5"]))
        self.assertFalse(util.contains(c, "bar"))
        self.assertFalse(util.contains(c, [2, 5, "bar"]))

        s = "1 2 3 asd qwe y(+)c f(+)(-) bar"
        self.assertTrue(util.contains(s, "y(+)c"))
        self.assertTrue(util.contains(s, ["asd", "qwe", "yxc"]))
        self.assertTrue(util.contains(s, ["sdf", "dfg", "qwe"]))
        self.assertFalse(util.contains(s, "tag1"))
        self.assertFalse(util.contains(s, ["tag1", "tag2", "tag3"]))

        self.assertTrue(util.contains(s, "(+)", ""))
        self.assertTrue(util.contains(s, ["(-)", "(+)"], ""))
        self.assertTrue(util.contains(s, "(+)", 0))
        self.assertTrue(util.contains(s, "(+)", False))

        self.assertFalse(util.contains(s, "(+)", None))
        self.assertTrue(util.contains(s, "y(+)c", None))
        self.assertTrue(util.contains(s, ["(-)", "(+)", "bar"], None))

        s = "1, 2, 3, asd, qwe, y(+)c, f(+)(-), bar"
        self.assertTrue(util.contains(s, "y(+)c", ", "))
        self.assertTrue(util.contains(s, ["sdf", "dfg", "qwe"], ", "))
        self.assertFalse(util.contains(s, "tag1", ", "))

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

    def test_identity(self):
        for value in (123, "foo", [1, 2, 3], (1, 2, 3), {1: 2}, None):
            self.assertIs(util.identity(value), value)

    def test_noop(self):
        self.assertEqual(util.noop(), None)

    def test_md5(self):
        self.assertEqual(util.md5(b""),
                         "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(util.md5(b"hello"),
                         "5d41402abc4b2a76b9719d911017c592")

        self.assertEqual(util.md5(""),
                         "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(util.md5("hello"),
                         "5d41402abc4b2a76b9719d911017c592")
        self.assertEqual(util.md5("ワルド"),
                         "051f29cd6c942cf110a0ccc5729871d2")

        self.assertEqual(util.md5(0),
                         "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(util.md5(()),
                         "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(util.md5(None),
                         "d41d8cd98f00b204e9800998ecf8427e")

    def test_sha1(self):
        self.assertEqual(util.sha1(b""),
                         "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(util.sha1(b"hello"),
                         "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")

        self.assertEqual(util.sha1(""),
                         "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(util.sha1("hello"),
                         "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")
        self.assertEqual(util.sha1("ワルド"),
                         "0cbe319081aa0e9298448ec2bb16df8c494aa04e")

        self.assertEqual(util.sha1(0),
                         "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(util.sha1(()),
                         "da39a3ee5e6b4b0d3255bfef95601890afd80709")
        self.assertEqual(util.sha1(None),
                         "da39a3ee5e6b4b0d3255bfef95601890afd80709")

    def test_import_file(self):
        module = util.import_file("datetime")
        self.assertIs(module, datetime)

        with tempfile.TemporaryDirectory() as path:
            file = path + "/module_test.py"
            with open(file, "w") as fp:
                fp.write("""
import datetime
key = "foobar"
value = 123
""")
            module = util.import_file(file)

        self.assertEqual(module.__name__, "module_test")
        self.assertEqual(module.key, "foobar")
        self.assertEqual(module.value, 123)
        self.assertIs(module.datetime, datetime)

    def test_build_duration_func(self, f=util.build_duration_func):

        def test_single(df, v):
            for _ in range(10):
                self.assertEqual(df(), v)

        def test_range(df, lower, upper):
            for __ in range(10):
                v = df()
                self.assertGreaterEqual(v, lower)
                self.assertLessEqual(v, upper)

        for v in (0, 0.0, "", None, (), []):
            self.assertIsNone(f(v))

        for v in (0, 0.0, "", None, (), []):
            test_single(f(v, 1.0), 1.0)

        test_single(f(3), 3)
        test_single(f(3.0), 3.0)
        test_single(f("3"), 3)
        test_single(f("3.0-"), 3)
        test_single(f("  3  -"), 3)

        test_range(f((2, 4)), 2, 4)
        test_range(f([2, 4]), 2, 4)
        test_range(f("2-4"), 2, 4)
        test_range(f("  2.0  - 4 "), 2, 4)

    def test_extractor_filter(self):
        # empty
        func = util.build_extractor_filter("")
        self.assertEqual(func(TestExtractor)      , True)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorAlt)   , True)

        # category
        func = util.build_extractor_filter("test_category")
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , True)

        # subcategory
        func = util.build_extractor_filter("*:test_subcategory")
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorAlt)   , False)

        # basecategory
        func = util.build_extractor_filter("test_basecategory")
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , False)

        # category-subcategory pair
        func = util.build_extractor_filter("test_category:test_subcategory")
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorAlt)   , True)

        # combination
        func = util.build_extractor_filter(
            ["test_category", "*:test_subcategory"])
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , False)

        # whitelist
        func = util.build_extractor_filter(
            "test_category:test_subcategory", negate=False)
        self.assertEqual(func(TestExtractor)      , True)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , False)

        func = util.build_extractor_filter(
            ["test_category:test_subcategory", "*:test_subcategory_parent"],
            negate=False)
        self.assertEqual(func(TestExtractor)      , True)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorAlt)   , False)

    def test_generate_token(self):
        tokens = set()
        for _ in range(100):
            token = util.generate_token()
            tokens.add(token)
            self.assertEqual(len(token), 16 * 2)
            self.assertRegex(token, r"^[0-9a-f]+$")
        self.assertGreaterEqual(len(tokens), 99)

        token = util.generate_token(80)
        self.assertEqual(len(token), 80 * 2)
        self.assertRegex(token, r"^[0-9a-f]+$")

    def test_format_value(self):
        self.assertEqual(util.format_value(0)         , "0")
        self.assertEqual(util.format_value(1)         , "1")
        self.assertEqual(util.format_value(12)        , "12")
        self.assertEqual(util.format_value(123)       , "123")
        self.assertEqual(util.format_value(1234)      , "1.23k")
        self.assertEqual(util.format_value(12345)     , "12.34k")
        self.assertEqual(util.format_value(123456)    , "123.45k")
        self.assertEqual(util.format_value(1234567)   , "1.23M")
        self.assertEqual(util.format_value(12345678)  , "12.34M")
        self.assertEqual(util.format_value(123456789) , "123.45M")
        self.assertEqual(util.format_value(1234567890), "1.23G")

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

    def test_enumerate_reversed(self):

        seq = [11, 22, 33]
        result = [(3, 33), (2, 22), (1, 11)]

        def gen():
            for i in seq:
                yield i

        def gen_2():
            yield from seq

        def assertEqual(it1, it2):
            ae = self.assertEqual
            for i1, i2 in itertools.zip_longest(it1, it2):
                ae(i1, i2)

        assertEqual(
            util.enumerate_reversed(seq), [(2, 33), (1, 22), (0, 11)])
        assertEqual(
            util.enumerate_reversed(seq, 1), result)
        assertEqual(
            util.enumerate_reversed(seq, 2), [(4, 33), (3, 22), (2, 11)])

        assertEqual(
            util.enumerate_reversed(gen(), 0, len(seq)),
            [(2, 33), (1, 22), (0, 11)])
        assertEqual(
            util.enumerate_reversed(gen(), 1, len(seq)), result)
        assertEqual(
            util.enumerate_reversed(gen_2(), 1, len(seq)), result)
        assertEqual(
            util.enumerate_reversed(gen_2(), 2, len(seq)),
            [(4, 33), (3, 22), (2, 11)])

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

    def test_datetime_to_timestamp(self, f=util.datetime_to_timestamp):
        self.assertEqual(f(util.EPOCH), 0.0)
        self.assertEqual(f(datetime.datetime(2010, 1, 1)), 1262304000.0)
        self.assertEqual(f(datetime.datetime(2010, 1, 1, 0, 0, 0, 128000)),
                         1262304000.128000)
        with self.assertRaises(TypeError):
            f(None)

    def test_datetime_to_timestamp_string(
            self, f=util.datetime_to_timestamp_string):
        self.assertEqual(f(util.EPOCH), "0")
        self.assertEqual(f(datetime.datetime(2010, 1, 1)), "1262304000")
        self.assertEqual(f(None), "")

    def test_datetime_from_timestamp(
            self, f=util.datetime_from_timestamp):
        self.assertEqual(f(0.0), util.EPOCH)
        self.assertEqual(f(1262304000.0), datetime.datetime(2010, 1, 1))
        self.assertEqual(f(1262304000.128000).replace(microsecond=0),
                         datetime.datetime(2010, 1, 1, 0, 0, 0))

    def test_datetime_utcfromtimestamp(
            self, f=util.datetime_utcfromtimestamp):
        self.assertEqual(f(0.0), util.EPOCH)
        self.assertEqual(f(1262304000.0), datetime.datetime(2010, 1, 1))

    def test_datetime_utcnow(
            self, f=util.datetime_utcnow):
        self.assertIsInstance(f(), datetime.datetime)

    def test_universal_none(self):
        obj = util.NONE

        self.assertFalse(obj)
        self.assertEqual(len(obj), 0)
        self.assertEqual(int(obj), 0)
        self.assertEqual(hash(obj), 0)

        self.assertEqual(str(obj), str(None))
        self.assertEqual(repr(obj), repr(None))
        self.assertEqual(format(obj), str(None))
        self.assertEqual(format(obj, "%F"), str(None))

        self.assertIs(obj.attr, obj)
        self.assertIs(obj["key"], obj)
        self.assertIs(obj(), obj)
        self.assertIs(obj(1, "a"), obj)
        self.assertIs(obj(foo="bar"), obj)
        self.assertIs(iter(obj), obj)
        self.assertEqual(util.json_dumps(obj), "null")

        self.assertLess(obj, "foo")
        self.assertLessEqual(obj, None)
        self.assertTrue(obj == obj)
        self.assertFalse(obj == 0)
        self.assertFalse(obj != obj)
        self.assertGreater(123, obj)
        self.assertGreaterEqual(1.23, obj)

        self.assertEqual(obj + 123, obj)
        self.assertEqual(obj - 123, obj)
        self.assertEqual(obj * 123, obj)
        #  self.assertEqual(obj @ 123, obj)
        self.assertEqual(obj / 123, obj)
        self.assertEqual(obj // 123, obj)
        self.assertEqual(obj % 123, obj)

        self.assertEqual(123 + obj, obj)
        self.assertEqual(123 - obj, obj)
        self.assertEqual(123 * obj, obj)
        #  self.assertEqual(123 @ obj, obj)
        self.assertEqual(123 / obj, obj)
        self.assertEqual(123 // obj, obj)
        self.assertEqual(123 % obj, obj)

        self.assertEqual(obj << 123, obj)
        self.assertEqual(obj >> 123, obj)
        self.assertEqual(obj & 123, obj)
        self.assertEqual(obj ^ 123, obj)
        self.assertEqual(obj | 123, obj)

        self.assertEqual(123 << obj, obj)
        self.assertEqual(123 >> obj, obj)
        self.assertEqual(123 & obj, obj)
        self.assertEqual(123 ^ obj, obj)
        self.assertEqual(123 | obj, obj)

        self.assertEqual(-obj, obj)
        self.assertEqual(+obj, obj)
        self.assertEqual(~obj, obj)
        self.assertEqual(abs(obj), obj)

        mapping = {}
        mapping[obj] = 123
        self.assertIn(obj, mapping)
        self.assertEqual(mapping[obj], 123)

        array = [1, 2, 3]
        self.assertEqual(array[obj], 1)

        if platform.python_implementation().lower() == "cpython":
            self.assertTrue(time.localtime(obj))

        i = 0
        for _ in obj:
            i += 1
        self.assertEqual(i, 0)

    def test_module_proxy(self):
        proxy = util.ModuleProxy()

        self.assertIs(proxy.os, os)
        self.assertIs(proxy.os.path, os.path)
        self.assertIs(proxy["os"], os)
        self.assertIs(proxy["os.path"], os.path)
        self.assertIs(proxy["os"].path, os.path)

        self.assertIs(proxy.abcdefghi, util.NONE)
        self.assertIs(proxy["abcdefghi"], util.NONE)
        self.assertIs(proxy["abc.def.ghi"], util.NONE)
        self.assertIs(proxy["os.path2"], util.NONE)

    def test_null_context(self):
        with util.NullContext():
            pass

        with util.NullContext() as ctx:
            self.assertIs(ctx, None)

        try:
            with util.NullContext() as ctx:
                exc_orig = ValueError()
                raise exc_orig
        except ValueError as exc:
            self.assertIs(exc, exc_orig)


class TestExtractor():
    category = "test_category"
    subcategory = "test_subcategory"
    basecategory = "test_basecategory"


class TestExtractorParent(TestExtractor):
    category = "test_category"
    subcategory = "test_subcategory_parent"


class TestExtractorAlt(TestExtractor):
    category = "test_category_alt"
    subcategory = "test_subcategory"


if __name__ == "__main__":
    unittest.main()
