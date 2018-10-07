#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.util as util
import gallery_dl.exception as exception
import sys
import random
import string


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


class TestFormatter(unittest.TestCase):

    kwdict = {
        "a": "hElLo wOrLd",
        "b": "äöü",
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

    def test_missing_custom_default(self):
        replacement = default = "foobar"
        self._run_test("{missing}"     , replacement, default)
        self._run_test("{missing.attr}", replacement, default)
        self._run_test("{missing[key]}", replacement, default)
        self._run_test("{missing:?a//}", "a" + default, default)

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
        self.assertRaises(Exception, util.raises(Exception()))

        func = util.raises(ValueError(1))
        self.assertRaises(Exception, func)
        self.assertRaises(Exception, func)
        self.assertRaises(Exception, func)

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


if __name__ == '__main__':
    unittest.main()
