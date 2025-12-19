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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import path, extractor, config  # noqa E402

KWDICT = {
    "category" : "test",
    "filename" : "file",
    "extension": "ext",
    "name"     : "test-テスト-'&>-/:~",
    "ext"      : "txt",
    "foo"      : "bar",
    "id"       : 123,
}


class TestPath(unittest.TestCase):

    def _pfmt(self, data={}, kwdict=False, extr=extractor.find("noop")):
        pathfmt = path.PathFormat(extr)

        if kwdict:
            pathfmt.set_directory({
                **(kwdict if isinstance(kwdict, dict) else KWDICT),
                **data,
            })

        return pathfmt

    def setUp(self):
        config.clear()
        path.WINDOWS = False


class TestPathObject(TestPath):

    def test_default(self):
        pfmt = self._pfmt()

        self.assertEqual(pfmt.kwdict, {})
        self.assertEqual(pfmt.delete, False)
        self.assertEqual(pfmt.filename, "")
        self.assertEqual(pfmt.extension, "")
        self.assertEqual(pfmt.directory, "")
        self.assertEqual(pfmt.realdirectory, "")
        self.assertEqual(pfmt.path, "")
        self.assertEqual(pfmt.realpath, "")
        self.assertEqual(pfmt.temppath, "")
        self.assertEqual(pfmt.basedirectory, "./gallery-dl/")
        self.assertEqual(pfmt.strip, "")

        self.assertIs(pfmt.filename_conditions, None)
        self.assertIs(pfmt.directory_conditions, None)

        self.assertTrue(callable(pfmt.extension_map))
        self.assertTrue(callable(pfmt.extension_map))
        self.assertTrue(callable(pfmt.extension_map))
        self.assertTrue(callable(pfmt.clean_segment))
        self.assertTrue(callable(pfmt.clean_path))

        self.assertTrue(callable(pfmt.filename_formatter))
        for fmt in pfmt.directory_formatters:
            self.assertTrue(callable(fmt))

    def test_str(self):
        pfmt = self._pfmt()
        self.assertEqual(str(pfmt), pfmt.realdirectory)
        self.assertEqual(str(pfmt), "")

        pfmt = self._pfmt()
        pfmt.set_directory(KWDICT)
        pfmt.set_filename(KWDICT)
        pfmt.build_path()
        self.assertEqual(str(pfmt), pfmt.realpath)
        self.assertEqual(str(pfmt), "./gallery-dl/test/file.ext")


class TestPathOptions(TestPath):

    def test_option_filename(self):
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname , "file.ext")

        config.set((), "filename", "foo.{foo}")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "foo.bar")

        config.set((), "filename", {
            "foo == 'baz'": "foo",
            "id % 2"      : "bar",
            ""            : "baz",
        })
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "bar")

    def test_option_directory(self):
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.directory    , "./gallery-dl/test/")
        self.assertEqual(pfmt.realdirectory, "./gallery-dl/test/")

        config.set((), "directory", ["{foo}", "bar"])
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.directory    , "./gallery-dl/bar/bar/")
        self.assertEqual(pfmt.realdirectory, "./gallery-dl/bar/bar/")

        config.set((), "directory", {
            "foo == 'baz'": ["a", "b", "c"],
            "id % 2"      : ["odd", "{id}"],
            ""            : ["{foo}", "bar"],
        })
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.directory    , "./gallery-dl/odd/123/")
        self.assertEqual(pfmt.realdirectory, "./gallery-dl/odd/123/")

    def test_option_basedirectory(self):
        config.set((), "base-directory", "{foo}")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.realdirectory, "{foo}/test/")

        config.set((), "base-directory", {
            "foo == 'baz'": "bar",
            "id % 2"      : "./odd",
            ""            : "./default",
        })
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.realdirectory, "./odd/test/")

    def test_option_keywordsdefault(self):
        config.set((), "directory", ["{baz}"])
        config.set((), "base-directory", "")

        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.realdirectory, "None/")

        config.set((), "keywords-default", "ND")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.realdirectory, "ND/")

        config.set((), "keywords-default", "")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(pfmt.realdirectory, "")

    def test_option_extensionmap_default(self):
        kwdict = KWDICT.copy()
        pfmt = self._pfmt()
        pfmt.set_filename(kwdict)
        self.assertEqual(pfmt.extension, "ext")

        pfmt.set_extension("jpg")
        self.assertEqual(pfmt.extension, "jpg")
        self.assertEqual(kwdict["extension"], "jpg")

        pfmt.set_extension("png")
        self.assertEqual(pfmt.extension, "png")
        self.assertEqual(kwdict["extension"], "png")

        pfmt.set_extension("jpeg")
        self.assertEqual(pfmt.extension, "jpg")
        self.assertEqual(kwdict["extension"], "jpg")

        for ext, repl in path.EXTENSION_MAP.items():
            pfmt.set_extension(ext)
            self.assertEqual(pfmt.extension, repl)
            self.assertEqual(kwdict["extension"], repl)

    def test_option_extensionmap_custom(self):
        extmap = {
            "bitmap": "bmp",
            "ping"  : "png",
            "jiff"  : "gif",
        }
        config.set((), "extension-map", extmap)

        kwdict = KWDICT.copy()
        pfmt = self._pfmt()
        pfmt.set_filename(kwdict)

        pfmt.set_extension("jpg")
        self.assertEqual(pfmt.extension, "jpg")
        self.assertEqual(kwdict["extension"], "jpg")

        pfmt.set_extension("ping")
        self.assertEqual(pfmt.extension, "png")
        self.assertEqual(kwdict["extension"], "png")

        for ext, repl in extmap.items():
            pfmt.set_extension(ext)
            self.assertEqual(pfmt.extension, repl)
            self.assertEqual(kwdict["extension"], repl)

        for ext, repl in path.EXTENSION_MAP.items():
            pfmt.set_extension(ext)
            self.assertNotEqual(pfmt.extension, repl)
            self.assertNotEqual(kwdict["extension"], repl)

    def test_option_pathrestrict(self):
        config.set((), "filename", "{name}.{ext}")

        config.set((), "path-restrict", "unix")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test-テスト-'&>-_:~.txt", "unix")

        config.set((), "path-restrict", "windows")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test-テスト-'&_-__~.txt", "windows")

        config.set((), "path-restrict", "ascii")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test____________.txt", "ascii")

        config.set((), "path-restrict", "ascii+")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test-___-'&_-__~.txt", "ascii+")

    def test_option_pathrestrict_custom(self):
        config.set((), "filename", "{name}.{ext}")

        config.set((), "path-restrict", "ts-")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "_e___テスト_'&>_/:~._x_", "custom str")

        config.set((), "path-restrict", {
            "t": "A",
            "s": "B",
            "-": "###",
            "/": "|"
        })
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "AeBA###テスト###'&>###|:~.AxA", "custom dict")

        config.set((), "path-restrict", {
            "a-z": "x",
            "テ": "te",
            "ス": "su",
            "ト": "to",
        })
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "xxxx-tesuto-'&>-/:~.xxx", "custom dict range")

    def test_option_pathreplace(self):
        config.set((), "filename", "{name}.{ext}")

        config.set((), "path-restrict", "unix")
        config.set((), "path-replace", "&")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test-テスト-'&>-&:~.txt", "&")

        config.set((), "path-restrict", "windows")
        config.set((), "path-replace", "***")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "test-テスト-'&***-******~.txt", "***")

    def test_option_pathremove(self):
        config.set((), "filename", "{name}.{ext}")

        config.set((), "path-remove", "-&/")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "testテスト'>_:~.txt")

        config.set((), "path-remove", "a-z0-9")
        fname = self._pfmt().build_filename(KWDICT)
        self.assertEqual(fname, "-テスト-'&>-_:~.")

    def test_option_pathstrip(self):
        config.set((), "directory", [" . {name}.{ext} . "])
        config.set((), "base-directory", "")
        config.set((), "path-restrict", "unix")

        config.set((), "path-strip", "unix")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(
            pfmt.realdirectory, ". test-テスト-'&>-_:~.txt ./", "unix")

        config.set((), "path-strip", "windows")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(
            pfmt.realdirectory, ". test-テスト-'&>-_:~.txt/", "windows")

        config.set((), "path-strip", "txt")
        pfmt = self._pfmt(kwdict=True)
        self.assertEqual(
            pfmt.realdirectory, ". test-テスト-'&>-_:~.txt ./", "custom")


if __name__ == "__main__":
    unittest.main()
