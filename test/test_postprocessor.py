#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
import collections
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, output, path  # noqa E402
from gallery_dl import postprocessor, config  # noqa E402
from gallery_dl.postprocessor.common import PostProcessor  # noqa E402


class MockPostprocessorModule(Mock):
    __postprocessor__ = "mock"


class FakeJob():

    def __init__(self, extr=extractor.find("generic:https://example.org/")):
        extr.directory_fmt = ("{category}",)
        self.extractor = extr
        self.pathfmt = path.PathFormat(extr)
        self.out = output.NullOutput()
        self.get_logger = logging.getLogger
        self.hooks = collections.defaultdict(list)

    def register_hooks(self, hooks, options):
        for hook, callback in hooks.items():
            self.hooks[hook].append(callback)


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

    @patch("builtins.__import__")
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

    def tearDown(self):
        self.job.hooks.clear()

    def _create(self, options=None, data=None):
        kwdict = {"category": "test", "filename": "file", "extension": "ext"}
        if options is None:
            options = {}
        if data is not None:
            kwdict.update(data)

        self.pathfmt = self.job.pathfmt
        self.pathfmt.set_directory(kwdict)
        self.pathfmt.set_filename(kwdict)
        self.pathfmt.build_path()

        pp = postprocessor.find(self.__class__.__name__[:-4].lower())
        return pp(self.job, options)

    def _trigger(self, events=None):
        for event in (events or ("prepare", "file")):
            for callback in self.job.hooks[event]:
                callback(self.pathfmt)


class ClassifyTest(BasePostprocessorTest):

    def test_classify_default(self):
        pp = self._create()

        self.assertEqual(pp.mapping, {
            ext: directory
            for directory, exts in pp.DEFAULT_MAPPING.items()
            for ext in exts
        })
        self.pathfmt.set_extension("jpg")
        self.pathfmt.build_path()

        pp.prepare(self.pathfmt)
        path = os.path.join(self.dir.name, "test", "Pictures")
        self.assertEqual(self.pathfmt.path, path + "/file.jpg")
        self.assertEqual(self.pathfmt.realpath, path + "/file.jpg")

        with patch("os.makedirs") as mkdirs:
            self._trigger()
            mkdirs.assert_called_once_with(path, exist_ok=True)

    def test_classify_noop(self):
        pp = self._create()
        rp = self.pathfmt.realpath

        pp.prepare(self.pathfmt)
        self.assertEqual(self.pathfmt.path, rp)
        self.assertEqual(self.pathfmt.realpath, rp)

        with patch("os.makedirs") as mkdirs:
            self._trigger()
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
        self.pathfmt.build_path()

        pp.prepare(self.pathfmt)
        path = os.path.join(self.dir.name, "test", "foo", "bar")
        self.assertEqual(self.pathfmt.path, path + "/file.foo")
        self.assertEqual(self.pathfmt.realpath, path + "/file.foo")

        with patch("os.makedirs") as mkdirs:
            self._trigger()
            mkdirs.assert_called_once_with(path, exist_ok=True)


class ExecTest(BasePostprocessorTest):

    def test_command_string(self):
        self._create({
            "command": "echo {} {_path} {_directory} {_filename} && rm {};",
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        p.assert_called_once_with(
            "echo {0} {0} {1} {2} && rm {0};".format(
                self.pathfmt.realpath,
                self.pathfmt.realdirectory,
                self.pathfmt.filename),
            shell=True)
        i.wait.assert_called_once_with()

    def test_command_list(self):
        self._create({
            "command": ["~/script.sh", "{category}",
                        "\fE _directory.upper()"],
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        p.assert_called_once_with(
            [
                os.path.expanduser("~/script.sh"),
                self.pathfmt.kwdict["category"],
                self.pathfmt.realdirectory.upper(),
            ],
            shell=False,
        )

    def test_command_returncode(self):
        self._create({
            "command": "echo {}",
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 123
            p.return_value = i

            with self.assertLogs() as log:
                self._trigger(("after",))

        msg = ("WARNING:postprocessor.exec:'echo {}' returned with "
               "non-zero exit status (123)".format(self.pathfmt.realpath))
        self.assertEqual(log.output[0], msg)

    def test_async(self):
        self._create({
            "async"  : True,
            "command": "echo {}",
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            p.return_value = i
            self._trigger(("after",))

        self.assertTrue(p.called)
        self.assertFalse(i.wait.called)


class MetadataTest(BasePostprocessorTest):

    def test_metadata_default(self):
        pp = self._create()

        # default arguments
        self.assertEqual(pp.write    , pp._write_json)
        self.assertEqual(pp.extension, "json")
        self.assertTrue(callable(pp._json_encode))

    def test_metadata_json(self):
        pp = self._create({
            "mode"      : "json",
            "extension" : "JSON",
        }, {
            "public"    : "hello ワールド",
            "_private"  : "foo バー",
        })

        self.assertEqual(pp.write    , pp._write_json)
        self.assertEqual(pp.extension, "JSON")
        self.assertTrue(callable(pp._json_encode))

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realpath + ".JSON"
        m.assert_called_once_with(path, "w", encoding="utf-8")

        if sys.hexversion >= 0x3060000:
            # python 3.4 & 3.5 have random order without 'sort: True'
            self.assertEqual(self._output(m), """{
    "category": "test",
    "filename": "file",
    "extension": "ext",
    "public": "hello ワールド"
}
""")

    def test_metadata_json_options(self):
        pp = self._create({
            "mode"      : "json",
            "ascii"     : True,
            "sort"      : True,
            "separators": [",", " : "],
            "private"   : True,
            "indent"    : None,
            "open"      : "a",
            "encoding"  : "UTF-8",
            "extension" : "JSON",
        }, {
            "public"    : "hello ワールド",
            "_private"  : "foo バー",
        })

        self.assertEqual(pp.write    , pp._write_json)
        self.assertEqual(pp.extension, "JSON")
        self.assertTrue(callable(pp._json_encode))

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realpath + ".JSON"
        m.assert_called_once_with(path, "a", encoding="UTF-8")
        self.assertEqual(self._output(m), """{\
"_private" : "foo \\u30d0\\u30fc",\
"category" : "test",\
"extension" : "ext",\
"filename" : "file",\
"public" : "hello \\u30ef\\u30fc\\u30eb\\u30c9"}
""")

    def test_metadata_tags(self):
        pp = self._create(
            {"mode": "tags"},
            {"tags": ["foo", "bar", "baz"]},
        )
        self.assertEqual(pp.write, pp._write_tags)
        self.assertEqual(pp.extension, "txt")

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realpath + ".txt"
        m.assert_called_once_with(path, "w", encoding="utf-8")
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_tags_split_1(self):
        self._create(
            {"mode": "tags"},
            {"tags": "foo, bar, baz"},
        )
        with patch("builtins.open", mock_open()) as m:
            self._trigger()
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_tags_split_2(self):
        self._create(
            {"mode": "tags"},
            {"tags": "foobar1 foobar2 foobarbaz"},
        )
        with patch("builtins.open", mock_open()) as m:
            self._trigger()
        self.assertEqual(self._output(m), "foobar1\nfoobar2\nfoobarbaz\n")

    def test_metadata_tags_tagstring(self):
        self._create(
            {"mode": "tags"},
            {"tag_string": "foo, bar, baz"},
        )
        with patch("builtins.open", mock_open()) as m:
            self._trigger()
        self.assertEqual(self._output(m), "foo\nbar\nbaz\n")

    def test_metadata_tags_dict(self):
        self._create(
            {"mode": "tags"},
            {"tags": {"g": ["foobar1", "foobar2"], "m": ["foobarbaz"]}},
        )
        with patch("builtins.open", mock_open()) as m:
            self._trigger()
        self.assertEqual(self._output(m), "foobar1\nfoobar2\nfoobarbaz\n")

    def test_metadata_tags_list_of_dict(self):
        self._create(
            {"mode": "tags"},
            {"tags": [
                {"g": "foobar1", "m": "foobar2", "u": True},
                {"g": None, "m": "foobarbaz", "u": [3, 4]},
            ]},
        )
        with patch("builtins.open", mock_open()) as m:
            self._trigger()
        self.assertEqual(self._output(m), "foobar1\nfoobar2\nfoobarbaz\n")

    def test_metadata_custom(self):
        def test(pp_info):
            pp = self._create(pp_info, {"foo": "bar"})
            self.assertEqual(pp.write, pp._write_custom)
            self.assertEqual(pp.extension, "txt")
            self.assertTrue(pp._content_fmt)

            with patch("builtins.open", mock_open()) as m:
                self._trigger()
            self.assertEqual(self._output(m), "bar\nNone\n")
            self.job.hooks.clear()

        test({"mode": "custom", "content-format": "{foo}\n{missing}\n"})
        test({"mode": "custom", "content-format": ["{foo}", "{missing}"]})
        test({"mode": "custom", "format": "{foo}\n{missing}\n"})
        test({"format": "{foo}\n{missing}\n"})

    def test_metadata_extfmt(self):
        pp = self._create({
            "extension"       : "ignored",
            "extension-format": "json",
        })

        self.assertEqual(pp._filename, pp._filename_extfmt)

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realdirectory + "file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_extfmt_2(self):
        self._create({
            "extension-format": "{extension!u}-data:{category:Res/ES/}",
        })

        self.pathfmt.prefix = "2."
        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realdirectory + "file.2.EXT-data:tESt"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_directory(self):
        self._create({
            "directory": "metadata",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realdirectory + "metadata/file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_directory_2(self):
        self._create({
            "directory"       : "metadata////",
            "extension-format": "json",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realdirectory + "metadata/file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_filename(self):
        self._create({
            "filename"        : "{category}_{filename}_/meta/\n\r.data",
            "extension-format": "json",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = self.pathfmt.realdirectory + "test_file__meta_.data"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_stdout(self):
        self._create({"filename": "-", "indent": None, "sort": True})

        with patch("sys.stdout", Mock()) as m:
            self._trigger()

        self.assertEqual(self._output(m), """\
{"category": "test", "extension": "ext", "filename": "file"}
""")

    def test_metadata_modify(self):
        kwdict = {"foo": 0, "bar": {"bax": 1, "bay": 2, "baz": 3, "ba2": {}}}
        self._create({
            "mode": "modify",
            "fields": {
                "foo"          : "{filename}-{foo!s}",
                "foo2"         : "\fE bar['bax'] + 122",
                "bar[\"baz\"]" : "{_now}",
                "bar['ba2'][a]": "test",
            },
        }, kwdict)

        pdict = self.pathfmt.kwdict
        self.assertIsNot(kwdict, pdict)
        self.assertEqual(pdict["foo"], kwdict["foo"])
        self.assertEqual(pdict["bar"], kwdict["bar"])

        self._trigger()

        self.assertEqual(pdict["foo"] , "file-0")
        self.assertEqual(pdict["foo2"], 123)
        self.assertEqual(pdict["bar"]["ba2"]["a"], "test")
        self.assertIsInstance(pdict["bar"]["baz"], datetime)

    def test_metadata_delete(self):
        kwdict = {
            "foo": 0,
            "bar": {
                "bax": 1,
                "bay": 2,
                "baz": {"a": 3, "b": 4},
            },
        }
        self._create({
            "mode": "delete",
            "fields": ["foo", "bar['bax']", "bar[\"baz\"][a]"],
        }, kwdict)

        pdict = self.pathfmt.kwdict
        self.assertIsNot(kwdict, pdict)

        self.assertEqual(pdict["foo"], kwdict["foo"])
        self.assertEqual(pdict["bar"], kwdict["bar"])

        self._trigger()

        self.assertNotIn("foo", pdict)
        self.assertNotIn("bax", pdict["bar"])
        self.assertNotIn("a", pdict["bar"]["baz"])

        # no errors for deleted/undefined fields
        self._trigger()
        self.assertNotIn("foo", pdict)
        self.assertNotIn("bax", pdict["bar"])
        self.assertNotIn("a", pdict["bar"]["baz"])

    def test_metadata_option_skip(self):
        self._create({"skip": True})

        with patch("builtins.open", mock_open()) as m, \
                patch("os.path.exists") as e:
            e.return_value = True
            self._trigger()

        self.assertTrue(e.called)
        self.assertTrue(not m.called)
        self.assertTrue(not len(self._output(m)))

        with patch("builtins.open", mock_open()) as m, \
                patch("os.path.exists") as e:
            e.return_value = False
            self._trigger()

        self.assertTrue(e.called)
        self.assertTrue(m.called)
        self.assertGreater(len(self._output(m)), 0)

        path = self.pathfmt.realdirectory + "file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8")

    def test_metadata_option_skip_false(self):
        self._create({"skip": False})

        with patch("builtins.open", mock_open()) as m, \
                patch("os.path.exists") as e:
            self._trigger()

        self.assertTrue(not e.called)
        self.assertTrue(m.called)

    @staticmethod
    def _output(mock):
        return "".join(
            call[1][0]
            for call in mock.mock_calls
            if call[0].endswith("write")
        )


class MtimeTest(BasePostprocessorTest):

    def test_mtime_datetime(self):
        self._create(None, {"date": datetime(1980, 1, 1)})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)

    def test_mtime_timestamp(self):
        self._create(None, {"date": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)

    def test_mtime_none(self):
        self._create(None, {"date": None})
        self._trigger()
        self.assertNotIn("_mtime", self.pathfmt.kwdict)

    def test_mtime_undefined(self):
        self._create(None, {})
        self._trigger()
        self.assertNotIn("_mtime", self.pathfmt.kwdict)

    def test_mtime_key(self):
        self._create({"key": "foo"}, {"foo": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)

    def test_mtime_value(self):
        self._create({"value": "{foo}"}, {"foo": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime"], 315532800)


class PythonTest(BasePostprocessorTest):

    def test_module(self):
        path = os.path.join(self.dir.name, "module.py")
        self._write_module(path)

        sys.path.insert(0, self.dir.name)
        try:
            self._create({"function": "module:calc"}, {"_value": 123})
        finally:
            del sys.path[0]

        self.assertNotIn("_result", self.pathfmt.kwdict)
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_result"], 246)

    def test_path(self):
        path = os.path.join(self.dir.name, "module.py")
        self._write_module(path)

        self._create({"function": path + ":calc"}, {"_value": 12})

        self.assertNotIn("_result", self.pathfmt.kwdict)
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_result"], 24)

    def _write_module(self, path):
        with open(path, "w") as fp:
            fp.write("""
def calc(kwdict):
    kwdict["_result"] = kwdict["_value"] * 2
""")


class ZipTest(BasePostprocessorTest):

    def test_zip_default(self):
        pp = self._create()
        self.assertEqual(self.job.hooks["file"][0], pp.write_fast)
        self.assertEqual(pp.path, self.pathfmt.realdirectory[:-1])
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            pp.path + ".zip", "a", zipfile.ZIP_STORED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.zip"))

    def test_zip_safe(self):
        pp = self._create({"mode": "safe"})
        self.assertEqual(self.job.hooks["file"][0], pp.write_safe)
        self.assertEqual(pp.path, self.pathfmt.realdirectory[:-1])
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            pp.path + ".zip", "a", zipfile.ZIP_STORED, True,
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
            pp.path + ".cbz", "a", zipfile.ZIP_DEFLATED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.cbz"))

    def test_zip_write(self):
        with tempfile.NamedTemporaryFile("w", dir=self.dir.name) as file:
            pp = self._create({"files": [file.name, "_info_.json"],
                               "keep-files": True})

            filename = os.path.basename(file.name)
            file.write("foobar\n")

            # write dummy file with 3 different names
            for i in range(3):
                name = "file{}.ext".format(i)
                self.pathfmt.temppath = file.name
                self.pathfmt.filename = name

                self._trigger()

                nti = pp.zfile.NameToInfo
                self.assertEqual(len(nti), i+2)
                self.assertIn(name, nti)

            # check file contents
            self.assertEqual(len(nti), 4)
            self.assertIn("file0.ext", nti)
            self.assertIn("file1.ext", nti)
            self.assertIn("file2.ext", nti)
            self.assertIn(filename, nti)

            # write the last file a second time (will be skipped)
            self._trigger()
            self.assertEqual(len(pp.zfile.NameToInfo), 4)

        # close file
        self._trigger(("finalize",))

        # reopen to check persistence
        with zipfile.ZipFile(pp.zfile.filename) as file:
            nti = file.NameToInfo
            self.assertEqual(len(pp.zfile.NameToInfo), 4)
            self.assertIn("file0.ext", nti)
            self.assertIn("file1.ext", nti)
            self.assertIn("file2.ext", nti)
            self.assertIn(filename, nti)

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
            self._trigger()

        # write the last file a second time (should be skipped)
        self._trigger()

        # close file
        self._trigger(("finalize",))

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
