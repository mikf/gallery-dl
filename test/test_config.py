#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import gallery_dl.config as config
import os
import tempfile


class TestConfig(unittest.TestCase):

    def setUp(self):
        config.set((), "a", "1")
        config.set((), "b", {
            "a": 2,
            "c": "text",
        })

    def tearDown(self):
        config.clear()

    def test_get(self):
        self.assertEqual(config.get(()        , "a")     , "1")
        self.assertEqual(config.get(("b",)    , "c")     , "text")
        self.assertEqual(config.get(()        , "d")     , None)
        self.assertEqual(config.get(("e", "f"), "g", 123), 123)

    def test_interpolate(self):
        self.assertEqual(config.interpolate(()    , "a")     , "1")
        self.assertEqual(config.interpolate(("b",), "a")     , "1")
        self.assertEqual(config.interpolate(("b",), "c", "2"), "text")
        self.assertEqual(config.interpolate(("b",), "d", "2"), "2")
        config.set((), "d", 123)
        self.assertEqual(config.interpolate(("b",), "d", "2"), 123)
        self.assertEqual(config.interpolate(("d",), "d", "2"), 123)

    def test_set(self):
        config.set(("b",)    , "c", [1, 2, 3])
        config.set(("e", "f"), "g", value=234)
        self.assertEqual(config.get(("b",)    , "c"), [1, 2, 3])
        self.assertEqual(config.get(("e", "f"), "g"), 234)

    def test_setdefault(self):
        config.setdefault(("b",)    , "c", [1, 2, 3])
        config.setdefault(("e", "f"), "g", value=234)
        self.assertEqual(config.get(("b",)    , "c"), "text")
        self.assertEqual(config.get(("e", "f"), "g"), 234)

    def test_unset(self):
        config.unset(()    , "a")
        config.unset(("b",), "c")
        config.unset(("c",), "d")
        self.assertEqual(config.get(()    , "a"), None)
        self.assertEqual(config.get(("b",), "a"), 2)
        self.assertEqual(config.get(("b",), "c"), None)

    def test_apply(self):
        options = (
            (("b",)    , "c", [1, 2, 3]),
            (("e", "f"), "g", 234),
        )

        self.assertEqual(config.get(("b",)    , "c"), "text")
        self.assertEqual(config.get(("e", "f"), "g"), None)

        with config.apply(options):
            self.assertEqual(config.get(("b",)    , "c"), [1, 2, 3])
            self.assertEqual(config.get(("e", "f"), "g"), 234)

        self.assertEqual(config.get(("b",)    , "c"), "text")
        self.assertEqual(config.get(("e", "f"), "g"), None)

    def test_load(self):
        with tempfile.TemporaryDirectory() as base:
            path1 = os.path.join(base, "cfg1")
            with open(path1, "w") as file:
                file.write('{"a": "1", "b": {"a": 2, "c": "text"}}')

            path2 = os.path.join(base, "cfg2")
            with open(path2, "w") as file:
                file.write('{"a": "7", "b": {"a": 8, "e": "foo"}}')

            config.load((path1,))
            self.assertEqual(config.get(()    , "a"), "1")
            self.assertEqual(config.get(("b",), "a"), 2)
            self.assertEqual(config.get(("b",), "c"), "text")

            config.load((path2,))
            self.assertEqual(config.get(()    , "a"), "7")
            self.assertEqual(config.get(("b",), "a"), 8)
            self.assertEqual(config.get(("b",), "c"), "text")
            self.assertEqual(config.get(("b",), "e"), "foo")

            config.clear()
            config.load((path1, path2))
            self.assertEqual(config.get(()    , "a"), "7")
            self.assertEqual(config.get(("b",), "a"), 8)
            self.assertEqual(config.get(("b",), "c"), "text")
            self.assertEqual(config.get(("b",), "e"), "foo")


if __name__ == '__main__':
    unittest.main()
