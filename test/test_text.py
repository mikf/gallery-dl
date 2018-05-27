#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest

from gallery_dl import text


INVALID = ((), [], {}, None, 1, 2.3)
INVALID_ALT = ((), [], {}, None, "")


class TestText(unittest.TestCase):

    def test_clean_xml(self, f=text.clean_xml):
        # standard usage
        self.assertEqual(f(""), "")
        self.assertEqual(f("foo"), "foo")
        self.assertEqual(f("\tfoo\nbar\r"), "\tfoo\nbar\r")
        self.assertEqual(f("<foo>\ab\ba\fr\v</foo>"), "<foo>bar</foo>")

        # 'repl' argument
        repl = "#"
        self.assertEqual(f("", repl), "")
        self.assertEqual(f("foo", repl), "foo")
        self.assertEqual(f("\tfoo\nbar\r", repl), "\tfoo\nbar\r")
        self.assertEqual(
            f("<foo>\ab\ba\fr\v</foo>", repl), "<foo>#b#a#r#</foo>")

        # removal of all illegal control characters
        value = "".join(chr(x) for x in range(32))
        self.assertEqual(f(value), "\t\n\r")

        # 'invalid' arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

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
        self.assertEqual(f(" Hello  World.  "), [" Hello  World.  "])
        self.assertEqual(f("Hello<br/>World."), result)
        self.assertEqual(
            f("<div><b class='a'>Hello</b><i>World.</i></div>"), result)

        # empty HTML
        self.assertEqual(f("<div></div>"), empty)
        self.assertEqual(f(" <div>   </div> "), empty)

        # malformed HTML
        self.assertEqual(f("<div</div>"), empty)
        self.assertEqual(f("<div<Hello World.</div>"), empty)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), empty)

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

    def test_nameext_from_url(self, f=text.nameext_from_url):
        empty = {"filename": "", "name": "", "extension": ""}
        result = {"filename": "filename.ext",
                  "name": "filename", "extension": "ext"}

        # standard usage
        self.assertEqual(f(""), empty)
        self.assertEqual(f("filename.ext"), result)
        self.assertEqual(f("/filename.ext"), result)
        self.assertEqual(f("example.org/filename.ext"), result)
        self.assertEqual(f("http://example.org/v2/filename.ext"), result)
        self.assertEqual(
            f("http://example.org/v2/filename.ext?param=value#frag"), result)

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), empty)

    def test_clean_path_windows(self, f=text.clean_path_windows):
        self.assertEqual(f(""), "")
        self.assertEqual(f("foo"), "foo")
        self.assertEqual(f("foo/bar"), "foo_bar")
        self.assertEqual(f("foo<>:\"\\/|?*bar"), "foo_________bar")

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

    def test_clean_path_posix(self, f=text.clean_path_posix):
        self.assertEqual(f(""), "")
        self.assertEqual(f("foo"), "foo")
        self.assertEqual(f("foo/bar"), "foo_bar")
        self.assertEqual(f("foo<>:\"\\/|?*bar"), "foo<>:\"\\_|?*bar")

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value), "")

    def test_extract(self, f=text.extract):
        txt = "<a><b>"
        self.assertEqual(f(txt, "<", ">"), ("a", 3))
        self.assertEqual(f(txt, "X", ">"), (None, 0))
        self.assertEqual(f(txt, "<", "X"), (None, 0))

        # 'pos' argument
        for i in range(1, 4):
            self.assertEqual(f(txt, "<", ">", i), ("b", 6))
        for i in range(4, 10):
            self.assertEqual(f(txt, "<", ">", i), (None, i))

        # invalid arguments
        for value in INVALID:
            self.assertEqual(f(value   , "<"  , ">")  , (None, 0))
            self.assertEqual(f(txt, value, ">")  , (None, 0))
            self.assertEqual(f(txt, "<"  , value), (None, 0))

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


if __name__ == '__main__':
    unittest.main()
