#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import sys

from gallery_dl import text


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
        for value in ((), [], {}, None, 1, 2.3):
            self.assertEqual(f(value), "")

    def test_remove_html(self):
        cases = (
            "Hello World.",
            " Hello  World. ",
            "Hello<br/>World.",
            "<div><span class='a'>Hello</span><strong>World.</strong></div>"
        )
        result = "Hello World."
        for case in cases:
            self.assertEqual(text.remove_html(case), result)

    def test_filename_from_url(self):
        cases = (
            "http://example.org/v2/filename.ext",
            "http://example.org/v2/filename.ext?param=value#fragment",
            "example.org/filename.ext",
            "/filename.ext",
            "filename.ext",
        )
        result = "filename.ext"
        for case in cases:
            self.assertEqual(text.filename_from_url(case), result)

    def test_nameext_from_url(self):
        cases = (
            "http://example.org/v2/filename.ext",
            "http://example.org/v2/filename.ext?param=value#fragment",
            "example.org/filename.ext",
            "/filename.ext",
            "filename.ext",
        )
        result = {
            "filename" : "filename.ext",
            "name"     : "filename",
            "extension": "ext",
        }
        for case in cases:
            self.assertEqual(text.nameext_from_url(case), result)

    def test_clean_path(self):
        cases = {
            "Hello World." : ("Hello World.", "Hello World."),
            "Hello/World/.": ("Hello_World_.", "Hello_World_."),
            r'<Hello>:|"World\*?': (
                '_Hello____World___', r'<Hello>:|"World\*?'
            ),
        }
        for case, result in cases.items():
            self.assertEqual(text.clean_path_windows(case), result[0])
            self.assertEqual(text.clean_path_posix(case), result[1])

    def test_shorten_path(self):
        cases = {
            "dirname": "dirname",
            "X"*255: "X"*255,
            "X"*256: "X"*255,
            "Ä"*255: "Ä"*127,
        }
        enc = sys.getfilesystemencoding()
        for case, result in cases.items():
            self.assertEqual(text.shorten_path(case), result)
            self.assertTrue(len(text.shorten_path(case).encode(enc)) <= 255)

    def test_shorten_filename(self):
        self.maxDiff = None
        cases = {
            "filename.ext": "filename.ext",
            "X"*251 + ".ext": "X"*251 + ".ext",
            "X"*255 + ".ext": "X"*251 + ".ext",
            "Ä"*251 + ".ext": "Ä"*125 + ".ext",
        }
        enc = sys.getfilesystemencoding()
        for case, result in cases.items():
            fname = text.shorten_filename(case)
            self.assertEqual(fname, result)
            self.assertTrue(len(fname.encode(enc)) <= 255)

    def test_extract(self):
        cases = {
            ("<a><b>", "<", ">")   : ("a", 3),
            ("<a><b>", "X", ">")   : (None, 0),
            ("<a><b>", "<", "X")   : (None, 0),
            ("<a><b>", "<", ">", 3): ("b", 6),
            ("<a><b>", "X", ">", 3): (None, 3),
            ("<a><b>", "<", "X", 3): (None, 3),
        }
        for case, result in cases.items():
            self.assertEqual(text.extract(*case), result)

    def test_extract_all(self):
        txt = "[c][b][a]: xyz! [d][e"
        result = ({
            "A": "a",
            "B": "b",
            "X": "xyz",
            "E": "xtra",
        }, 15)
        self.assertEqual(text.extract_all(txt, (
            (None, "[", "]"),
            ("B" , "[", "]"),
            ("A" , "[", "]"),
            ("X" , ": ", "!"),
        ), values={"E": "xtra"}), result)

    def test_extract_iter(self):
        txt = "[c][b][a]: xyz! [d][e"
        result = ["c", "b", "a", "d"]
        self.assertEqual(list(text.extract_iter(txt, "[", "]")), result)

    def test_parse_query(self):
        # standard stuff
        self.assertEqual(
            text.parse_query(""), {})
        self.assertEqual(
            text.parse_query("foo=1"), {"foo": "1"})
        self.assertEqual(
            text.parse_query("foo=1&bar=2"), {"foo": "1", "bar": "2"})

        # missing value
        self.assertEqual(
            text.parse_query("bar"), {})
        self.assertEqual(
            text.parse_query("foo=1&bar"), {"foo": "1"})
        self.assertEqual(
            text.parse_query("foo=1&bar&baz=3"), {"foo": "1", "baz": "3"})

        # keys with identical names
        self.assertEqual(
            text.parse_query("foo=1&foo=2"), {"foo": "1"})
        self.assertEqual(
            text.parse_query("foo=1&bar=2&foo=3&bar=4"),
            {"foo": "1", "bar": "2"},
        )

        # non-string arguments
        self.assertEqual(text.parse_query(()), {})
        self.assertEqual(text.parse_query([]), {})
        self.assertEqual(text.parse_query({}), {})
        self.assertEqual(text.parse_query(None), {})


if __name__ == '__main__':
    unittest.main()
