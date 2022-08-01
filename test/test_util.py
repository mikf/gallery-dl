#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
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
import datetime
import itertools
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
            jar = http.cookiejar.CookieJar()
            util.cookiestxt_load(io.StringIO(content, None), jar)
            for c, e in zip(jar, expected):
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
            util.cookiestxt_load("example.org\tTRUE\t/\tTRUE\t0\tname",
                                 http.cookiejar.CookieJar())

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

    def test_compile_expression(self):
        expr = util.compile_expression("1 + 2 * 3")
        self.assertEqual(expr(), 7)
        self.assertEqual(expr({"a": 1, "b": 2, "c": 3}), 7)
        self.assertEqual(expr({"a": 9, "b": 9, "c": 9}), 7)

        expr = util.compile_expression("a + b * c")
        self.assertEqual(expr({"a": 1, "b": 2, "c": 3}), 7)
        self.assertEqual(expr({"a": 9, "b": 9, "c": 9}), 90)

        with self.assertRaises(NameError):
            expr()
        with self.assertRaises(NameError):
            expr({"a": 2})

        with self.assertRaises(SyntaxError):
            util.compile_expression("")
        with self.assertRaises(SyntaxError):
            util.compile_expression("x++")

        expr = util.compile_expression("1 and abort()")
        with self.assertRaises(exception.StopExtraction):
            expr()

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

    def test_universal_none(self):
        obj = util.NONE

        self.assertFalse(obj)
        self.assertEqual(str(obj), str(None))
        self.assertEqual(repr(obj), repr(None))
        self.assertIs(obj.attr, obj)
        self.assertIs(obj["key"], obj)


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


if __name__ == '__main__':
    unittest.main()
