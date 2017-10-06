#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.util as util
import gallery_dl.exception as exception
import sys


class TestRange(unittest.TestCase):

    def test_parse_range(self):
        self.assertEqual(
            util.parse_range(""),
            [])
        self.assertEqual(
            util.parse_range("1-2"),
            [(1, 2)])
        self.assertEqual(
            util.parse_range("-"),
            [(1, sys.maxsize)])
        self.assertEqual(
            util.parse_range("-2,4,6-8,10-"),
            [(1, 2), (4, 4), (6, 8), (10, sys.maxsize)])
        self.assertEqual(
            util.parse_range(" - 3 , 4-  4, 2-6"),
            [(1, 3), (4, 4), (2, 6)])

    def test_optimize_range(self):
        self.assertEqual(
            util.optimize_range([]),
            [])
        self.assertEqual(
            util.optimize_range([(2, 4)]),
            [(2, 4)])
        self.assertEqual(
            util.optimize_range([(2, 4), (6, 8), (10, 12)]),
            [(2, 4), (6, 8), (10, 12)])
        self.assertEqual(
            util.optimize_range([(2, 4), (4, 6), (5, 8)]),
            [(2, 8)])
        self.assertEqual(
            util.optimize_range([(1, 1), (2, 2), (3, 6), (8, 9)]),
            [(1, 6), (8, 9)])


class TestPredicate(unittest.TestCase):

    def test_range_predicate(self):
        dummy = None

        pred = util.RangePredicate(util.parse_range(" - 3 , 4-  4, 2-6"))
        for i in range(6):
            self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

        pred = util.RangePredicate(util.parse_range("1, 3, 5"))
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        self.assertFalse(pred(dummy, dummy))
        self.assertTrue(pred(dummy, dummy))
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

        pred = util.RangePredicate(util.parse_range(""))
        with self.assertRaises(exception.StopExtraction):
            bool(pred(dummy, dummy))

    def test_unique_predicate(self):
        dummy = None

        pred = util.UniquePredicate()
        self.assertTrue(pred("1", dummy))
        self.assertTrue(pred("2", dummy))
        self.assertFalse(pred("1", dummy))
        self.assertFalse(pred("2", dummy))
        self.assertTrue(pred("3", dummy))
        self.assertFalse(pred("3", dummy))

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

    def _run_test(self, format_string, result):
        formatter = util.Formatter()
        output = formatter.vformat(format_string, self.kwdict)
        self.assertEqual(output, result, format_string)


class TestOther(unittest.TestCase):

    def test_bdecode(self):
        self.assertEqual(util.bdecode(""), 0)
        self.assertEqual(util.bdecode("123"), 123)
        self.assertEqual(util.bdecode("1111011", "01"), 123)
        self.assertEqual(util.bdecode("AAAABAA", "BA"), 123)

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

    def test_safe_int(self):
        self.assertEqual(util.safe_int(123), 123)
        self.assertEqual(util.safe_int("123"), 123)
        self.assertEqual(util.safe_int("zzz"), 0)
        self.assertEqual(util.safe_int(""), 0)
        self.assertEqual(util.safe_int(None), 0)
        self.assertEqual(util.safe_int("zzz", "default"), "default")
        self.assertEqual(util.safe_int("", "default"), "default")
        self.assertEqual(util.safe_int(None, "default"), "default")


if __name__ == '__main__':
    unittest.main()
