#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import dt # noqa E402


class TestDatetime(unittest.TestCase):

    def test_convert(self, f=dt.convert):

        def _assert(value, expected):
            result = f(value)
            self.assertIsInstance(result, datetime.datetime)
            self.assertEqual(result, expected, msg=repr(value))

        d = datetime.datetime(2010, 1, 1)
        self.assertIs(f(d), d)

        _assert(d             , d)
        _assert(1262304000    , d)
        _assert(1262304000.0  , d)
        _assert(1262304000.123, d)
        _assert("1262304000"  , d)

        _assert("2010-01-01"                      , d)
        _assert("2010-01-01 00:00:00"             , d)
        _assert("2010-01-01T00:00:00"             , d)
        _assert("2010-01-01T00:00:00.123456"      , d)
        _assert("2009-12-31T19:00:00-05:00"       , d)
        _assert("2009-12-31T19:00:00.123456-05:00", d)
        _assert("2010-01-01T00:00:00Z"            , d)
        _assert("2010-01-01T00:00:00.123456Z"     , d)
        _assert("2009-12-31T19:00:00-0500"        , d)
        _assert("2009-12-31T19:00:00.123456-0500" , d)

        _assert(0    , dt.NONE)
        _assert(""   , dt.NONE)
        _assert("foo", dt.NONE)
        _assert(None , dt.NONE)
        _assert(()   , dt.NONE)
        _assert([]   , dt.NONE)
        _assert({}   , dt.NONE)
        _assert((1, 2, 3), dt.NONE)

    @unittest.skipIf(sys.hexversion < 0x30b0000,
                     "extended fromisoformat timezones")
    def test_convert_tz(self, f=dt.convert):

        def _assert(value, expected):
            result = f(value)
            self.assertIsInstance(result, datetime.datetime)
            self.assertEqual(result, expected, msg=repr(value))

        d = datetime.datetime(2010, 1, 1)
        _assert("2009-12-31T19:00:00-05"          , d)
        _assert("2009-12-31T19:00:00.123456-05"   , d)

    def test_to_timestamp(self, f=dt.to_ts):
        self.assertEqual(f(dt.EPOCH), 0.0)
        self.assertEqual(f(datetime.datetime(2010, 1, 1)), 1262304000.0)
        self.assertEqual(f(datetime.datetime(2010, 1, 1, 0, 0, 0, 128000)),
                         1262304000.128000)
        with self.assertRaises(TypeError):
            f(None)

    def test_to_timestamp_string(self, f=dt.to_ts_string):
        self.assertEqual(f(dt.EPOCH), "0")
        self.assertEqual(f(datetime.datetime(2010, 1, 1)), "1262304000")
        self.assertEqual(f(None), "")

    def test_from_timestamp(self, f=dt.from_ts):
        self.assertEqual(f(0.0), dt.EPOCH)
        self.assertEqual(f(1262304000.0), datetime.datetime(2010, 1, 1))
        self.assertEqual(f(1262304000.128000).replace(microsecond=0),
                         datetime.datetime(2010, 1, 1, 0, 0, 0))

    def test_now(self, f=dt.now):
        self.assertIsInstance(f(), datetime.datetime)

    def test_parse_timestamp(self, f=dt.parse_ts):
        null = dt.from_ts(0)
        value = dt.from_ts(1555816235)

        self.assertEqual(f(0)           , null)
        self.assertEqual(f("0")         , null)
        self.assertEqual(f(1555816235)  , value)
        self.assertEqual(f("1555816235"), value)

        for value in ((), [], {}, None, ""):
            self.assertEqual(f(value), dt.NONE)
            self.assertEqual(f(value, "foo"), "foo")

    def test_parse(self, f=dt.parse):
        self.assertEqual(
            f("1970.01.01", "%Y.%m.%d"),
            dt.EPOCH,
        )
        self.assertEqual(
            f("May 7, 2019 9:33 am", "%B %d, %Y %I:%M %p"),
            datetime.datetime(2019, 5, 7, 9, 33, 0),
        )
        self.assertEqual(
            f("2019-05-07T21:25:02.753+0900", "%Y-%m-%dT%H:%M:%S.%f%z"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )

        for value in ((), [], {}, None, 1, 2.3):
            self.assertEqual(f(value, "%Y"), dt.NONE)

    def test_parse_iso(self, f=dt.parse_iso):
        self.assertEqual(
            f("1970-01-01T00:00:00+00:00"),
            dt.from_ts(0),
        )
        self.assertEqual(
            f("2019-05-07T21:25:02+09:00"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07T12:25:02Z"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07 21:25:02"),
            datetime.datetime(2019, 5, 7, 21, 25, 2),
        )
        self.assertEqual(
            f("1970-01-01"),
            dt.EPOCH,
        )
        self.assertEqual(
            f("1970.01.01"),
            dt.NONE,
        )
        self.assertEqual(
            f("1970-01-01T00:00:00+0000"),
            dt.EPOCH,
        )
        self.assertEqual(
            f("2019-05-07T21:25:02.753+0900"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )

        for value in ((), [], {}, None, 1, 2.3):
            self.assertEqual(f(value), dt.NONE)

    def test_none(self):
        self.assertFalse(dt.NONE)
        self.assertIsInstance(dt.NONE, dt.datetime)
        self.assertEqual(str(dt.NONE), "[Invalid DateTime]")


if __name__ == "__main__":
    unittest.main()
