#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import text  # noqa E402


INVALID = ((), [], {}, None, 1, 2.3)
INVALID_ALT = ((), [], {}, None, "")


class TestText(unittest.TestCase):

    def test_remove_html(self, f=text.remove_html):
        result = "Hello World."

        # standard usage
        self.assertEqual(f(""), "")
        self.assertEqual(f("Hello World."), result)
        self.assertEqual(f(" Hello  World.  "), result)
        self.assertEqual(f("Hello<br/>World."), result)
        self.assertEqual(
            f("<div><b class='a'>Hello</b><i>World.</i></div>"), result)

        # empty HTML
        self.assertEqual(f("<div></div>"), "")
        self.assertEqual(f(" <div>   </div> "), "")

        # malformed HTML
        self.assertEqual(f("<div</div>"), "")
        self.assertEqual(f("<div<Hello World.</div>"), "")

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

    def test_split_html(self, f=text.split_html):
        result = ["Hello", "World."]
        empty = []

        # standard usage
        self.assertEqual(f(""), empty)
        self.assertEqual(f("Hello World."), ["Hello World."])
        self.assertEqual(f(" Hello  World.  "), ["Hello  World."])
        self.assertEqual(f("Hello<br/>World."), result)
        self.assertEqual(f(" Hello <br/> World.  "), result)
        self.assertEqual(
            f("<div><b class='a'>Hello</b><i>World.</i></div>"), result)

        # escaped HTML entities
        self.assertEqual(
            f("<i>&lt;foo&gt;</i> <i>&lt;bar&gt; </i>"), ["<foo>", "<bar>"])

        # empty HTML
        self.assertEqual(f("<div></div>"), empty)
        self.assertEqual(f(" <div>   </div> "), empty)

        # malformed HTML
        self.assertEqual(f("<div</div>"), empty)
        self.assertEqual(f("<div<Hello World.</div>"), empty)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), empty)

    def test_ensure_http_scheme(self, f=text.ensure_http_scheme):
        result = "https://example.org/filename.ext"

        # standard usage
        self.assertEqual(f(""), "")
        self.assertEqual(f("example.org/filename.ext"), result)
        self.assertEqual(f("/example.org/filename.ext"), result)
        self.assertEqual(f("//example.org/filename.ext"), result)
        self.assertEqual(f("://example.org/filename.ext"), result)

        # no change
        self.assertEqual(f(result), result)
        self.assertEqual(
            f("http://example.org/filename.ext"),
            "http://example.org/filename.ext",
        )

        # ...
        self.assertEqual(
            f("htp://example.org/filename.ext"),
            "https://htp://example.org/filename.ext",
        )

        # invalid arguments
        for value in INVALID_ALT:
            self.assertEqual(f(value), value)

    def test_filename_from_url(self, f=text.filename_from_url):
        result = "filename.ext"

        # standard usage
        self.assertEqual(f(""), "")
        self.assertEqual(f("filename.ext"), result)
        self.assertEqual(f("/filename.ext"), result)
        self.assertEqual(f("example.org/filename.ext"), result)
        self.assertEqual(f("http://example.org/v2/filename.ext"), result)
        self.assertEqual(
            f("http://example.org/v2/filename.ext?param=value#frag"), result)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

    def test_ext_from_url(self, f=text.ext_from_url):
        result = "ext"

        # standard usage
        self.assertEqual(f(""), "")
        self.assertEqual(f("filename"), "")
        self.assertEqual(f("filename.ext"), result)
        self.assertEqual(f("/filename.ExT"), result)
        self.assertEqual(f("example.org/filename.ext"), result)
        self.assertEqual(f("http://example.org/v2/filename.ext"), result)
        self.assertEqual(
            f("http://example.org/v2/filename.ext?param=value#frag"), result)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

    def test_nameext_from_url(self, f=text.nameext_from_url):
        empty = {"filename": "", "extension": ""}
        result = {"filename": "filename", "extension": "ext"}

        # standard usage
        self.assertEqual(f(""), empty)
        self.assertEqual(f("filename.ext"), result)
        self.assertEqual(f("/filename.ExT"), result)
        self.assertEqual(f("example.org/filename.ext"), result)
        self.assertEqual(f("http://example.org/v2/filename.ext"), result)
        self.assertEqual(
            f("http://example.org/v2/filename.ext?param=value#frag"), result)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), empty)

    def test_extract(self, f=text.extract):
        txt = "<a><b>"
        self.assertEqual(f(txt, "<", ">"), ("a" , 3))
        self.assertEqual(f(txt, "X", ">"), (None, 0))
        self.assertEqual(f(txt, "<", "X"), (None, 0))

        # 'pos' argument
        for i in range(1, 4):
            self.assertEqual(f(txt, "<", ">", i), ("b", 6))
        for i in range(4, 10):
            self.assertEqual(f(txt, "<", ">", i), (None, i))

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value, "<"  , ">")  , (None, 0))
            self.assertEqual(f(txt  , value, ">")  , (None, 0))
            self.assertEqual(f(txt  , "<"  , value), (None, 0))

    def test_rextract(self, f=text.rextract):
        txt = "<a><b>"
        self.assertEqual(f(txt, "<", ">"), ("b" , 3))
        self.assertEqual(f(txt, "X", ">"), (None, -1))
        self.assertEqual(f(txt, "<", "X"), (None, -1))

        # 'pos' argument
        for i in range(10, 3, -1):
            self.assertEqual(f(txt, "<", ">", i), ("b", 3))
        for i in range(3, 0, -1):
            self.assertEqual(f(txt, "<", ">", i), ("a", 0))

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value, "<"  , ">")  , (None, -1))
            self.assertEqual(f(txt  , value, ">")  , (None, -1))
            self.assertEqual(f(txt  , "<"  , value), (None, -1))

    def test_extract_all(self, f=text.extract_all):
        txt = "[c][b][a]: xyz! [d][e"

        self.assertEqual(
            f(txt, ()), ({}, 0))
        self.assertEqual(
            f(txt, (("C", "[", "]"), ("B", "[", "]"), ("A", "[", "]"))),
            ({"A": "a", "B": "b", "C": "c"}, 9),
        )

        # 'None' as field name
        self.assertEqual(
            f(txt, ((None, "[", "]"), (None, "[", "]"), ("A", "[", "]"))),
            ({"A": "a"}, 9),
        )
        self.assertEqual(
            f(txt, ((None, "[", "]"), (None, "[", "]"), (None, "[", "]"))),
            ({}, 9),
        )

        # failed matches
        self.assertEqual(
            f(txt, (("C", "[", "]"), ("X", "X", "X"), ("B", "[", "]"))),
            ({"B": "b", "C": "c", "X": None}, 6),
        )

        # 'pos' argument
        self.assertEqual(
            f(txt, (("B", "[", "]"), ("A", "[", "]")), pos=1),
            ({"A": "a", "B": "b"}, 9),
        )

        # 'values' argument
        self.assertEqual(
            f(txt, (("C", "[", "]"),), values={"A": "a", "B": "b"}),
            ({"A": "a", "B": "b", "C": "c"}, 3),
        )

        vdict = {}
        rdict, pos = f(txt, (), values=vdict)
        self.assertIs(vdict, rdict)

    def test_extract_iter(self, f=text.extract_iter):
        txt = "[c][b][a]: xyz! [d][e"

        def g(*args):
            return list(f(*args))

        self.assertEqual(
            g("", "[", "]"), [])
        self.assertEqual(
            g("[a]", "[", "]"), ["a"])
        self.assertEqual(
            g(txt, "[", "]"), ["c", "b", "a", "d"])
        self.assertEqual(
            g(txt, "X", "X"), [])
        self.assertEqual(
            g(txt, "[", "]", 6), ["a", "d"])

    def test_extract_from(self, f=text.extract_from):
        txt = "[c][b][a]: xyz! [d][e"

        e = f(txt)
        self.assertEqual(e("[", "]"), "c")
        self.assertEqual(e("[", "]"), "b")
        self.assertEqual(e("[", "]"), "a")
        self.assertEqual(e("[", "]"), "d")
        self.assertEqual(e("[", "]"), "")
        self.assertEqual(e("[", "]"), "")

        e = f(txt, pos=6, default="END")
        self.assertEqual(e("[", "]"), "a")
        self.assertEqual(e("[", "]"), "d")
        self.assertEqual(e("[", "]"), "END")
        self.assertEqual(e("[", "]"), "END")

    def test_parse_unicode_escapes(self, f=text.parse_unicode_escapes):
        self.assertEqual(f(""), "")
        self.assertEqual(f("foobar"), "foobar")
        self.assertEqual(f("foo’bar"), "foo’bar")
        self.assertEqual(f("foo\\u2019bar"), "foo’bar")
        self.assertEqual(f("foo\\u201bar"), "foo‛ar")
        self.assertEqual(f("foo\\u201zar"), "foo\\u201zar")
        self.assertEqual(
            f("\\u2018foo\\u2019\\u2020bar\\u00ff"),
            "‘foo’†barÿ",
        )

    def test_parse_bytes(self, f=text.parse_bytes):
        self.assertEqual(f("0"), 0)
        self.assertEqual(f("50"), 50)
        self.assertEqual(f("50k"), 50 * 1024**1)
        self.assertEqual(f("50m"), 50 * 1024**2)
        self.assertEqual(f("50g"), 50 * 1024**3)
        self.assertEqual(f("50t"), 50 * 1024**4)
        self.assertEqual(f("50p"), 50 * 1024**5)

        # fractions
        self.assertEqual(f("123.456"), 123)
        self.assertEqual(f("123.567"), 124)
        self.assertEqual(f("0.5M"), round(0.5 * 1024**2))

        # invalid arguments
        for value in INVALID_ALT:
            self.assertEqual(f(value), 0)
        self.assertEqual(f("NaN"), 0)
        self.assertEqual(f("invalid"), 0)
        self.assertEqual(f(" 123 kb "), 0)

    def test_parse_int(self, f=text.parse_int):
        self.assertEqual(f(0), 0)
        self.assertEqual(f("0"), 0)
        self.assertEqual(f(123), 123)
        self.assertEqual(f("123"), 123)

        # invalid arguments
        for value in INVALID_ALT:
            self.assertEqual(f(value), 0)
        self.assertEqual(f("123.456"), 0)
        self.assertEqual(f("zzz"), 0)
        self.assertEqual(f([1, 2, 3]), 0)
        self.assertEqual(f({1: 2, 3: 4}), 0)

        # 'default' argument
        default = "default"
        for value in INVALID_ALT:
            self.assertEqual(f(value, default), default)
        self.assertEqual(f("zzz", default), default)

    def test_parse_float(self, f=text.parse_float):
        self.assertEqual(f(0), 0.0)
        self.assertEqual(f("0"), 0.0)
        self.assertEqual(f(123), 123.0)
        self.assertEqual(f("123"), 123.0)
        self.assertEqual(f(123.456), 123.456)
        self.assertEqual(f("123.456"), 123.456)

        # invalid arguments
        for value in INVALID_ALT:
            self.assertEqual(f(value), 0.0)
        self.assertEqual(f("zzz"), 0.0)
        self.assertEqual(f([1, 2, 3]), 0.0)
        self.assertEqual(f({1: 2, 3: 4}), 0.0)

        # 'default' argument
        default = "default"
        for value in INVALID_ALT:
            self.assertEqual(f(value, default), default)
        self.assertEqual(f("zzz", default), default)

    def test_parse_query(self, f=text.parse_query):
        # standard usage
        self.assertEqual(f(""), {})
        self.assertEqual(f("foo=1"), {"foo": "1"})
        self.assertEqual(f("foo=1&bar=2"), {"foo": "1", "bar": "2"})

        # missing value
        self.assertEqual(f("bar"), {})
        self.assertEqual(f("foo=1&bar"), {"foo": "1"})
        self.assertEqual(f("foo=1&bar&baz=3"), {"foo": "1", "baz": "3"})

        # keys with identical names
        self.assertEqual(f("foo=1&foo=2"), {"foo": "1"})
        self.assertEqual(
            f("foo=1&bar=2&foo=3&bar=4"),
            {"foo": "1", "bar": "2"},
        )

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), {})

    def test_parse_timestamp(self, f=text.parse_timestamp):
        null = datetime.datetime.utcfromtimestamp(0)
        value = datetime.datetime.utcfromtimestamp(1555816235)

        self.assertEqual(f(0)           , null)
        self.assertEqual(f("0")         , null)
        self.assertEqual(f(1555816235)  , value)
        self.assertEqual(f("1555816235"), value)

        for value in INVALID_ALT:
            self.assertEqual(f(value), None)
            self.assertEqual(f(value, "foo"), "foo")

    def test_parse_datetime(self, f=text.parse_datetime):
        null = datetime.datetime.utcfromtimestamp(0)

        self.assertEqual(f("1970-01-01T00:00:00+00:00"), null)
        self.assertEqual(f("1970-01-01T00:00:00+0000") , null)
        self.assertEqual(f("1970.01.01", "%Y.%m.%d")   , null)

        self.assertEqual(
            f("2019-05-07T21:25:02+09:00"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07T21:25:02+0900"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07T21:25:02.753+0900", "%Y-%m-%dT%H:%M:%S.%f%z"),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07T21:25:02", "%Y-%m-%dT%H:%M:%S", utcoffset=9),
            datetime.datetime(2019, 5, 7, 12, 25, 2),
        )
        self.assertEqual(
            f("2019-05-07 21:25:02"),
            "2019-05-07 21:25:02",
        )

        for value in INVALID:
            self.assertEqual(f(value), None)
        self.assertEqual(f("1970.01.01"), "1970.01.01")


if __name__ == '__main__':
    unittest.main()
