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

import tempfile

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOTDIR)
from gallery_dl import config, util  # noqa E402


class TestConfig(unittest.TestCase):

    def setUp(self):
        config.set(()        , "a", 1)
        config.set(("b",)    , "a", 2)
        config.set(("b", "b"), "a", 3)
        config.set(("b",)    , "c", "text")
        config.set(("b", "b"), "c", [8, 9])

    def tearDown(self):
        config.clear()

    def test_get(self):
        self.assertEqual(config.get(()        , "a")   , 1)
        self.assertEqual(config.get(("b",)    , "a")   , 2)
        self.assertEqual(config.get(("b", "b"), "a")   , 3)

        self.assertEqual(config.get(()        , "c")   , None)
        self.assertEqual(config.get(("b",)    , "c")   , "text")
        self.assertEqual(config.get(("b", "b"), "c")   , [8, 9])

        self.assertEqual(config.get(("a",)    , "g")   , None)
        self.assertEqual(config.get(("a", "a"), "g")   , None)
        self.assertEqual(config.get(("e", "f"), "g")   , None)
        self.assertEqual(config.get(("e", "f"), "g", 4), 4)

    def test_interpolate(self):
        self.assertEqual(config.interpolate(()        , "a"), 1)
        self.assertEqual(config.interpolate(("b",)    , "a"), 1)
        self.assertEqual(config.interpolate(("b", "b"), "a"), 1)

        self.assertEqual(config.interpolate(()        , "c"), None)
        self.assertEqual(config.interpolate(("b",)    , "c"), "text")
        self.assertEqual(config.interpolate(("b", "b"), "c"), [8, 9])

        self.assertEqual(config.interpolate(("a",)    , "g")   , None)
        self.assertEqual(config.interpolate(("a", "a"), "g")   , None)
        self.assertEqual(config.interpolate(("e", "f"), "g")   , None)
        self.assertEqual(config.interpolate(("e", "f"), "g", 4), 4)

        self.assertEqual(config.interpolate(("b",), "d", 1) , 1)
        self.assertEqual(config.interpolate(("d",), "d", 1) , 1)
        config.set(()    , "d", 2)
        self.assertEqual(config.interpolate(("b",), "d", 1) , 2)
        self.assertEqual(config.interpolate(("d",), "d", 1) , 2)
        config.set(("b",), "d", 3)
        self.assertEqual(config.interpolate(("b",), "d", 1) , 2)
        self.assertEqual(config.interpolate(("d",), "d", 1) , 2)

    def test_interpolate_common(self):

        def lookup():
            return config.interpolate_common(
                ("Z1", "Z2"), (
                    ("A1", "A2"),
                    ("B1",),
                    ("C1", "C2", "C3"),
                ), "KEY", "DEFAULT",
            )

        def test(path, value, expected=None):
            config.set(path, "KEY", value)
            self.assertEqual(lookup(), expected or value)

        self.assertEqual(lookup(), "DEFAULT")
        test(("Z1",), 1)
        test(("Z1", "Z2"), 2)
        test(("Z1", "Z2", "C1"), 3)
        test(("Z1", "Z2", "C1", "C2"), 4)
        test(("Z1", "Z2", "C1", "C2", "C3"), 5)
        test(("Z1", "Z2", "B1"), 6)
        test(("Z1", "Z2", "A1"), 7)
        test(("Z1", "Z2", "A1", "A2"), 8)
        test(("Z1", "A1", "A2"), 999, 8)
        test(("Z1", "Z2", "A1", "A2", "A3"), 999, 8)
        test((), 9)

    def test_accumulate(self):
        self.assertEqual(config.accumulate((), "l"), [])

        config.set(()        , "l", [5, 6])
        config.set(("c",)    , "l", [3, 4])
        config.set(("c", "c"), "l", [1, 2])
        self.assertEqual(
            config.accumulate((), "l")        , [5, 6])
        self.assertEqual(
            config.accumulate(("c",), "l")    , [3, 4, 5, 6])
        self.assertEqual(
            config.accumulate(("c", "c"), "l"), [1, 2, 3, 4, 5, 6])

        config.set(("c",), "l", None)
        config.unset(("c", "c"), "l")
        self.assertEqual(
            config.accumulate((), "l")        , [5, 6])
        self.assertEqual(
            config.accumulate(("c",), "l")    , [5, 6])
        self.assertEqual(
            config.accumulate(("c", "c"), "l"), [5, 6])

        config.set(()        , "l", 4)
        config.set(("c",)    , "l", [2, 3])
        config.set(("c", "c"), "l", 1)
        self.assertEqual(
            config.accumulate((), "l")        , [4])
        self.assertEqual(
            config.accumulate(("c",), "l")    , [2, 3, 4])
        self.assertEqual(
            config.accumulate(("c", "c"), "l"), [1, 2, 3, 4])

        config.set(("c",), "l", None)
        self.assertEqual(
            config.accumulate((), "l")        , [4])
        self.assertEqual(
            config.accumulate(("c",), "l")    , [4])
        self.assertEqual(
            config.accumulate(("c", "c"), "l"), [1, 4])

    def test_set(self):
        config.set(()        , "c", [1, 2, 3])
        config.set(("b",)    , "c", [1, 2, 3])
        config.set(("e", "f"), "g", value=234)
        self.assertEqual(config.get(()        , "c"), [1, 2, 3])
        self.assertEqual(config.get(("b",)    , "c"), [1, 2, 3])
        self.assertEqual(config.get(("e", "f"), "g"), 234)

    def test_setdefault(self):
        config.setdefault(()        , "c", [1, 2, 3])
        config.setdefault(("b",)    , "c", [1, 2, 3])
        config.setdefault(("e", "f"), "g", value=234)
        self.assertEqual(config.get(()        , "c"), [1, 2, 3])
        self.assertEqual(config.get(("b",)    , "c"), "text")
        self.assertEqual(config.get(("e", "f"), "g"), 234)

    def test_unset(self):
        config.unset(()    , "a")
        config.unset(("b",), "c")
        config.unset(("a",), "d")
        config.unset(("b",), "d")
        config.unset(("c",), "d")
        self.assertEqual(config.get(()    , "a"), None)
        self.assertEqual(config.get(("b",), "a"), 2)
        self.assertEqual(config.get(("b",), "c"), None)
        self.assertEqual(config.get(("a",), "d"), None)
        self.assertEqual(config.get(("b",), "d"), None)
        self.assertEqual(config.get(("c",), "d"), None)

    def test_apply(self):
        options = (
            (("b",)    , "c", [1, 2, 3]),
            (("e", "f"), "g", 234),
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
            with open(path1, "w") as fp:
                fp.write('{"a": 1, "b": {"a": 2, "c": "text"}}')

            path2 = os.path.join(base, "cfg2")
            with open(path2, "w") as fp:
                fp.write('{"a": 7, "b": {"a": 8, "e": "foo"}}')

            config.clear()
            config.load((path1,))
            self.assertEqual(config.get(()    , "a"), 1)
            self.assertEqual(config.get(("b",), "a"), 2)
            self.assertEqual(config.get(("b",), "c"), "text")

            config.load((path2,))
            self.assertEqual(config.get(()    , "a"), 7)
            self.assertEqual(config.get(("b",), "a"), 8)
            self.assertEqual(config.get(("b",), "c"), "text")
            self.assertEqual(config.get(("b",), "e"), "foo")

            config.clear()
            config.load((path1, path2))
            self.assertEqual(config.get(()    , "a"), 7)
            self.assertEqual(config.get(("b",), "a"), 8)
            self.assertEqual(config.get(("b",), "c"), "text")
            self.assertEqual(config.get(("b",), "e"), "foo")


class TestConfigFiles(unittest.TestCase):

    def test_default_config(self):
        cfg = self._load("gallery-dl.conf")
        self.assertIsInstance(cfg, dict)
        self.assertTrue(cfg)

    def test_example_config(self):
        cfg = self._load("gallery-dl-example.conf")
        self.assertIsInstance(cfg, dict)
        self.assertTrue(cfg)

    @staticmethod
    def _load(name):
        path = os.path.join(ROOTDIR, "docs", name)
        try:
            with open(path) as fp:
                return util.json_loads(fp.read())
        except FileNotFoundError:
            raise unittest.SkipTest(path + " not available")


if __name__ == "__main__":
    unittest.main()
