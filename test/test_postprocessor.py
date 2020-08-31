#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import Mock, mock_open, patch

import logging
import zipfile
import tempfile
from datetime import datetime, timezone as tz

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, output, util  # noqa E402
from gallery_dl import postprocessor, util, config  # noqa E402
from gallery_dl.postprocessor.common import PostProcessor  # noqa E402


class MockPostprocessorModule(Mock):
    __postprocessor__ = "mock"


class FakeJob():

    def __init__(self):
        self.extractor = extractor.find("test:")
        self.pathfmt = util.PathFormat(self.extractor)
        self.out = output.NullOutput()
        self.get_logger = logging.getLogger


class TestPostprocessorModule(unittest.TestCase):

    def setUp(self):
        postprocessor._cache.clear()

    def test_find(self):
        for name in (postprocessor.modules):
            cls = postprocessor.find(name)
            self.assertEqual(cls.__name__, name.capitalize() + "PP")
            self.assertIs(cls.__base__, PostProcessor)

        self.assertEqual(postprocessor.find("foo"), None)
        self.assertEqual(postprocessor.find(1234) , None)
        self.assertEqual(postprocessor.find(None) , None)

    @patch("importlib.import_module")
    def test_cache(self, import_module):
        import_module.return_value = MockPostprocessorModule()

        for name in (postprocessor.modules):
            postprocessor.find(name)
        self.assertEqual(import_module.call_count, len(postprocessor.modules))

        # no new calls to import_module
        for name in (postprocessor.modules):
            postprocessor.find(name)
        self.assertEqual(import_module.call_count, len(postprocessor.modules))


class BasePostprocessorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        config.set((), "base-directory", cls.dir.name)
        cls.job = FakeJob()

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()
        config.clear()

    def _create(self, options=None, data=None):
        kwdict = {"category": "test", "filename": "file", "extension": "ext"}
        if options is None:
            options = {}
        if data is not None:
            kwdict.update(data)

        self.pathfmt = self.job.pathfmt
        self.pathfmt.set_directory(kwdict)
        self.pathfmt.set_filename(kwdict)

        pp = postprocessor.find(self.__class__.__name__[:-4].lower())
        return pp(self.job, options)


class ClassifyTest(BasePostprocessorTest):

    def test_classify_default(self):
        pp = self._create()

        self.assertEqual(pp.mapping, {
            ext: directory
            for directory, exts in pp.DEFAULT_MAPPING.items()
            for ext in exts
        })
        self.pathfmt.set_extension("jpg")

        pp.prepare(self.pathfmt)
        path = os.path.join(self.dir.name, "test", "Pictures")
        self.assertEqual(self.pathfmt.path, path + "/file.jpg")
        self.assertEqual(self.pathfmt.realpath, path + "/file.jpg")

        with patch("os.makedirs") as mkdirs:
            pp.run(self.pathfmt)
            mkdirs.assert_called_once_with(path, exist_ok=True)

    def test_classify_noop(self):
        pp = self._create()
        rp = self.pathfmt.realpath

        pp.prepare(self.pathfmt)
        self.assertEqual(self.pathfmt.path, rp)
        self.assertEqual(self.pathfmt.realpath, rp)

        with patch("os.makedirs") as mkdirs:
            pp.run(self.pathfmt)
            self.assertEqual(mkdirs.call_count, 0)

    def test_classify_custom(self):
        pp = self._create({"mapping": {
            "foo/bar": ["foo", "bar"],
        }})

        self.assertEqual(pp.mapping, {
            "foo": "foo/bar",
            "bar": "foo/bar",
        })
        self.pathfmt.set_extension("foo")

        pp.prepare(self.pathfmt)
        path = os.path.join(self.dir.name, "test", "foo", "bar")
        self.assertEqual(self.pathfmt.path, path + "/file.foo")
        self.assertEqual(self.pathfmt.realpath, path + "/file.foo")

        with patch("os.makedirs") as mkdirs:
            pp.run(self.pathfmt)
            mkdirs.assert_called_once_with(path, exist_ok=True)


class MetadataTest(BasePostprocessorTest):

    def test_metadata_default(self):
        pp = self._create()

        # default arguments
        self.assertEqual(pp.write    , pp._write_json)
        self.assertEqual(pp.ascii    , False)
        self.assertEqual(pp.indent   , 4)
        self.assertEqual(pp.extension, "json")

    def test_metadata_json(self):
        pp = self._create({
            "mode"     : "json",
            "ascii"    : True,
            "indent"   : 2,
            "extension": "JSON",
        }, {
            "public"   : "hello",
            "_private" : "world",
        })

        self.assertEqual(pp.write    , pp._write_json)
        self.assertEqual(pp.ascii    , True)
        self.assertEqual(pp.indent   , 2)
        self.assertEqual(pp.extension, "JSON")

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realpath + ".JSON"
        m.assert_called_once_with(path, "w", encoding="utf-8")
        self.assertEqual(self._output(m), """{
  "category": "test",
  "extension": "ext",
  "filename": "file",
  "public": "hello"
}
""")

    def test_metadata_tags(self):
        pp = self._create(
            {"mode": "tags"},
            {"tags": ["foo", "bar", "baz"]},
        )
        self.assertEqual(pp.write, pp._write_tags)
        self.assertEqual(pp.extension, "txt")

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realpath + ".txt"
        m.assert_called_once_with(path, "w", encoding="utf-8")
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_tags_split_1(self):
        pp = self._create(
            {"mode": "tags"},
            {"tags": "foo, bar, baz"},
        )
        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_tags_split_2(self):
        pp = self._create(
            {"mode": "tags"},
            {"tags": "foobar1 foobar2 foobarbaz"},
        )
        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)
        self.assertEqual(self._output(m), "foobar1\nfoobar2\nfoobarbaz\n")

    def test_metadata_tags_tagstring(self):
        pp = self._create(
            {"mode": "tags"},
            {"tag_string": "foo, bar, baz"},
        )
        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_custom(self):
        pp = self._create(
            {"mode": "custom", "format": "{foo}\n{missing}\n"},
            {"foo": "bar"},
        )
        self.assertEqual(pp.write, pp._write_custom)
        self.assertEqual(pp.extension, "txt")
        self.assertTrue(pp.contentfmt)

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)
        self.assertEqual(self._output(m), "bar\nNone\n")

    def test_metadata_extfmt(self):
        pp = self._create({
            "extension"       : "ignored",
            "extension-format": "json",
        })

        self.assertEqual(pp._filename, pp._filename_custom)

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realdirectory + "file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_extfmt_2(self):
        pp = self._create({
            "extension-format": "{extension!u}-data:{category:Res/ES/}",
        })

        self.pathfmt.prefix = "2."
        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realdirectory + "file.2.EXT-data:tESt"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_directory(self):
        pp = self._create({
            "directory": "metadata",
        })

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realdirectory + "metadata/file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_directory_2(self):
        pp = self._create({
            "directory"       : "metadata////",
            "extension-format": "json",
        })

        with patch("builtins.open", mock_open()) as m:
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        path = self.pathfmt.realdirectory + "metadata/file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    @staticmethod
    def _output(mock):
        return "".join(
            call[1][0]
            for call in mock.mock_calls
            if call[0] == "().write"
        )


class MtimeTest(BasePostprocessorTest):

    def test_mtime_default(self):
        pp = self._create()
        self.assertEqual(pp.key, "date")

    def test_mtime_datetime(self):
        pp = self._create(None, {"date": datetime(1980, 1, 1, tzinfo=tz.utc)})
        pp.prepare(self.pathfmt)
        pp.run(self.pathfmt)
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)

    def test_mtime_timestamp(self):
        pp = self._create(None, {"date": 315532800})
        pp.prepare(self.pathfmt)
        pp.run(self.pathfmt)
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)

    def test_mtime_custom(self):
        pp = self._create({"key": "foo"}, {"foo": 315532800})
        pp.prepare(self.pathfmt)
        pp.run(self.pathfmt)
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)


class ZipTest(BasePostprocessorTest):

    def test_zip_default(self):
        pp = self._create()
        self.assertEqual(pp.path, self.pathfmt.realdirectory)
        self.assertEqual(pp.run, pp._write)
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            pp.path[:-1] + ".zip", "a", zipfile.ZIP_STORED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.zip"))

    def test_zip_safe(self):
        pp = self._create({"mode": "safe"})
        self.assertEqual(pp.path, self.pathfmt.realdirectory)
        self.assertEqual(pp.run, pp._write_safe)
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            pp.path[:-1] + ".zip", "a", zipfile.ZIP_STORED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.zip"))

    def test_zip_options(self):
        pp = self._create({
            "keep-files": True,
            "compression": "zip",
            "extension": "cbz",
        })
        self.assertEqual(pp.delete, False)
        self.assertEqual(pp.args, (
            pp.path[:-1] + ".cbz", "a", zipfile.ZIP_DEFLATED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.cbz"))

    def test_zip_write(self):
        pp = self._create()

        with tempfile.NamedTemporaryFile("w", dir=self.dir.name) as file:
            file.write("foobar\n")

            # write dummy file with 3 different names
            for i in range(3):
                name = "file{}.ext".format(i)
                self.pathfmt.temppath = file.name
                self.pathfmt.filename = name

                pp.prepare(self.pathfmt)
                pp.run(self.pathfmt)

                nti = pp.zfile.NameToInfo
                self.assertEqual(len(nti), i+1)
                self.assertIn(name, nti)

            # check file contents
            self.assertEqual(len(nti), 3)
            self.assertIn("file0.ext", nti)
            self.assertIn("file1.ext", nti)
            self.assertIn("file2.ext", nti)

            # write the last file a second time (will be skipped)
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)
            self.assertEqual(len(pp.zfile.NameToInfo), 3)

        # close file
        pp.run_final(self.pathfmt, 0)

        # reopen to check persistence
        with zipfile.ZipFile(pp.zfile.filename) as file:
            nti = file.NameToInfo
            self.assertEqual(len(pp.zfile.NameToInfo), 3)
            self.assertIn("file0.ext", pp.zfile.NameToInfo)
            self.assertIn("file1.ext", pp.zfile.NameToInfo)
            self.assertIn("file2.ext", pp.zfile.NameToInfo)

        os.unlink(pp.zfile.filename)

    def test_zip_write_mock(self):

        def side_effect(_, name):
            pp.zfile.NameToInfo.add(name)

        pp = self._create()
        pp.zfile = Mock()
        pp.zfile.NameToInfo = set()
        pp.zfile.write.side_effect = side_effect

        # write 3 files
        for i in range(3):
            self.pathfmt.temppath = self.pathfmt.realdirectory + "file.ext"
            self.pathfmt.filename = "file{}.ext".format(i)
            pp.prepare(self.pathfmt)
            pp.run(self.pathfmt)

        # write the last file a second time (will be skipped)
        pp.prepare(self.pathfmt)
        pp.run(self.pathfmt)

        pp.run_final(self.pathfmt, 0)

        self.assertEqual(pp.zfile.write.call_count, 3)
        for call in pp.zfile.write.call_args_list:
            args, kwargs = call
            self.assertEqual(len(args), 2)
            self.assertEqual(len(kwargs), 0)
            self.assertEqual(args[0], self.pathfmt.temppath)
            self.assertRegex(args[1], r"file\d\.ext")
        self.assertEqual(pp.zfile.close.call_count, 1)


if __name__ == "__main__":
    unittest.main()
