#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import Mock, mock_open, patch, call

import shutil
import logging
import zipfile
import tempfile
import collections
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, output, path, util, exception  # noqa E402
from gallery_dl import postprocessor, config, archive  # noqa E402
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

    def register_hooks(self, hooks, options=None):
        for hook, callback in hooks.items():
            self.hooks[hook].append(callback)


class TestPostprocessorModule(unittest.TestCase):

    def setUp(self):
        postprocessor._cache.clear()

    def test_find(self):
        for name in (postprocessor.modules):
            cls = postprocessor.find(name)
            self.assertEqual(cls.__name__, f"{name.capitalize()}PP")
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
        config.clear()
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

        self.assertEqual(pp.directory, "")
        self._trigger(("post",))
        self.assertEqual(pp.directory, self.pathfmt.directory)

        self.pathfmt.set_extension("jpg")
        self._trigger(("prepare",))
        self.pathfmt.build_path()
        path = os.path.join(self.dir.name, "test", "Pictures")
        self.assertEqual(self.pathfmt.path, f"{path}/file.jpg")
        self.assertEqual(self.pathfmt.realpath, f"{path}/file.jpg")

        self.pathfmt.set_extension("mp4")
        self._trigger(("prepare",))
        self.pathfmt.build_path()
        path = os.path.join(self.dir.name, "test", "Video")
        self.assertEqual(self.pathfmt.path, f"{path}/file.mp4")
        self.assertEqual(self.pathfmt.realpath, f"{path}/file.mp4")

    def test_classify_noop(self):
        pp = self._create()
        rp = self.pathfmt.realpath

        self.assertEqual(pp.directory, "")
        self._trigger(("post",))
        self._trigger(("prepare",))

        self.assertEqual(pp.directory, self.pathfmt.directory)
        self.assertEqual(self.pathfmt.path, rp)
        self.assertEqual(self.pathfmt.realpath, rp)

    def test_classify_custom(self):
        pp = self._create({"mapping": {
            "foo/bar": ["foo", "bar"],
        }})

        self.assertEqual(pp.mapping, {
            "foo": "foo/bar",
            "bar": "foo/bar",
        })

        self.assertEqual(pp.directory, "")
        self._trigger(("post",))
        self.assertEqual(pp.directory, self.pathfmt.directory)

        self.pathfmt.set_extension("foo")
        self._trigger(("prepare",))
        self.pathfmt.build_path()
        path = os.path.join(self.dir.name, "test", "foo", "bar")
        self.assertEqual(self.pathfmt.path, f"{path}/file.foo")
        self.assertEqual(self.pathfmt.realpath, f"{path}/file.foo")


class DirectoryTest(BasePostprocessorTest):

    def test_default(self):
        self._create()

        path = os.path.join(self.dir.name, "test")
        self.assertEqual(self.pathfmt.realdirectory, f"{path}/")
        self.assertEqual(self.pathfmt.realpath, f"{path}/file.ext")

        self.pathfmt.kwdict["category"] = "custom"
        self._trigger()

        path = os.path.join(self.dir.name, "custom")
        self.assertEqual(self.pathfmt.realdirectory, f"{path}/")
        self.pathfmt.build_path()
        self.assertEqual(self.pathfmt.realpath, f"{path}/file.ext")


class ExecTest(BasePostprocessorTest):

    def test_command_string(self):
        self._create({
            "command": "echo {} {_path} {_temppath} {_directory} {_filename} "
                       "&& rm {};",
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        p.assert_called_once_with(
            (f"echo "
             f"{self.pathfmt.realpath} "
             f"{self.pathfmt.realpath} "
             f"{self.pathfmt.temppath} "
             f"{self.pathfmt.realdirectory} "
             f"{self.pathfmt.filename} "
             f"&& rm {self.pathfmt.realpath};"),
            shell=True,
            creationflags=0,
            start_new_session=False,
        )
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
            creationflags=0,
            start_new_session=False,
        )

    def test_command_many(self):
        self._create({
            "commands": [
                "echo {} {_path} {_temppath} {_directory} {_filename} "
                "&& rm {};",
                ["~/script.sh", "{category}", "\fE _directory.upper()"],
            ]
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        self.assertEqual(p.call_args_list, [
            call(
                (f"echo "
                 f"{self.pathfmt.realpath} "
                 f"{self.pathfmt.realpath} "
                 f"{self.pathfmt.temppath} "
                 f"{self.pathfmt.realdirectory} "
                 f"{self.pathfmt.filename} "
                 f"&& rm {self.pathfmt.realpath};"),
                shell=True,
                creationflags=0,
                start_new_session=False,
            ),
            call(
                [
                    os.path.expanduser("~/script.sh"),
                    self.pathfmt.kwdict["category"],
                    self.pathfmt.realdirectory.upper(),
                ],
                shell=False,
                creationflags=0,
                start_new_session=False,
            ),
        ])

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

        msg = (f"WARNING:postprocessor.exec:"
               f"'echo {self.pathfmt.realpath}' "
               f"returned with non-zero exit status (123)")
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

    @unittest.skipIf(util.WINDOWS, "not POSIX")
    def test_session_posix(self):
        self._create({
            "session": True,
            "command": ["echo", "foobar"],
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        p.assert_called_once_with(
            ["echo", "foobar"],
            shell=False,
            creationflags=0,
            start_new_session=True,
        )
        i.wait.assert_called_once_with()

    @unittest.skipIf(not util.WINDOWS, "not Windows")
    def test_session_windows(self):
        self._create({
            "session": True,
            "command": ["echo", "foobar"],
        })

        with patch("gallery_dl.util.Popen") as p:
            i = Mock()
            i.wait.return_value = 0
            p.return_value = i
            self._trigger(("after",))

        import subprocess
        p.assert_called_once_with(
            ["echo", "foobar"],
            shell=False,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            start_new_session=False,
        )
        i.wait.assert_called_once_with()

    def test_archive(self):
        pp = self._create({
            "command": ["echo", "foobar"],
            "archive": ":memory:",
            "event"  : "finalize",
        })

        self.assertIsInstance(pp.archive, archive.DownloadArchive)

        with patch.object(pp.archive, "add") as m_aa, \
                patch.object(pp.archive, "close") as m_ac:
            self._trigger(("finalize",))
        pp.archive.close()

        m_aa.assert_called_once_with(self.pathfmt.kwdict)
        m_ac.assert_called_once()

    def test_verbose_string(self):
        self._create({
            "command": "echo foo bar",
            "verbose": False,
        })

        with patch("gallery_dl.util.Popen") as p, \
                self.assertLogs(level=10) as log_info:
            i = Mock()
            i.wait.return_value = 123
            p.return_value = i
            self._trigger(("after",))

        msg = "DEBUG:postprocessor.exec:Running 'echo'"
        self.assertEqual(log_info.output[0], msg)
        self.assertIn("'echo' returned with non-zero ", log_info.output[1])

    def test_verbose_list(self):
        self._create({
            "command": ["echo", "foo", "bar"],
            "verbose": False,
        })

        with patch("gallery_dl.util.Popen") as p, \
                self.assertLogs(level=10) as log_info:
            i = Mock()
            i.wait.return_value = 123
            p.return_value = i
            self._trigger(("after",))

        msg = "DEBUG:postprocessor.exec:Running 'echo'"
        self.assertEqual(log_info.output[0], msg)
        self.assertIn("'echo' returned with non-zero ", log_info.output[1])


class HashTest(BasePostprocessorTest):

    def test_default(self):
        self._create({})

        with self.pathfmt.open() as fp:
            fp.write(b"Foo Bar\n")

        self._trigger()

        kwdict = self.pathfmt.kwdict
        self.assertEqual(
            "35c9c9c7c90ad764bae9e2623f522c24", kwdict["md5"], "md5")
        self.assertEqual(
            "14d3d804494ef4e57d72de63e4cfee761240471a", kwdict["sha1"], "sha1")

    def test_custom_hashes(self):
        self._create({"hashes": "sha256:a,sha512:b"})

        with self.pathfmt.open() as fp:
            fp.write(b"Foo Bar\n")

        self._trigger()

        kwdict = self.pathfmt.kwdict
        self.assertEqual(
            "4775b55be17206445d7015a5fc7656f38a74b880670523c3b175455f885f2395",
            kwdict["a"], "sha256")
        self.assertEqual(
            "6028f9e6957f4ca929941318c4bba6258713fd5162f9e33bd10e1c456d252700"
            "3e1095b50736c4fd1e2deea152e3c8ecd5993462a747208e4d842659935a1c62",
            kwdict["b"], "sha512")

    def test_custom_hashes_dict(self):
        self._create({"hashes": {"a": "sha256", "b": "sha512"}})

        with self.pathfmt.open() as fp:
            fp.write(b"Foo Bar\n")

        self._trigger()

        kwdict = self.pathfmt.kwdict
        self.assertEqual(
            "4775b55be17206445d7015a5fc7656f38a74b880670523c3b175455f885f2395",
            kwdict["a"], "sha256")
        self.assertEqual(
            "6028f9e6957f4ca929941318c4bba6258713fd5162f9e33bd10e1c456d252700"
            "3e1095b50736c4fd1e2deea152e3c8ecd5993462a747208e4d842659935a1c62",
            kwdict["b"], "sha512")


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

        path = f"{self.pathfmt.realpath}.JSON"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

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
            "newline"   : "\r\n",
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

        path = f"{self.pathfmt.realpath}.JSON"
        m.assert_called_once_with(path, "a", encoding="UTF-8", newline='\r\n')
        # Since we mocked the call to open,
        # we don't actually see the effect of setting newline.
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

        path = f"{self.pathfmt.realpath}.txt"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)
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

    def test_metadata_mode_print(self):
        self._create(
            {"mode": "print", "format": "{foo}\n{missing}"},
            {"foo": "bar"},
        )

        with patch("sys.stdout", Mock()) as m:
            self._trigger()

        self.assertEqual(self._output(m), "bar\nNone\n")

    def test_metadata_extfmt(self):
        pp = self._create({
            "extension"       : "ignored",
            "extension-format": "json",
        })

        self.assertEqual(pp._filename, pp._filename_extfmt)

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_extfmt_2(self):
        self._create({
            "extension-format": "{extension!u}-data:{category:Res/ES/}",
        })

        self.pathfmt.prefix = "2."
        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}file.2.EXT-data:tESt"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_directory(self):
        self._create({
            "directory": "metadata",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}metadata/file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_directory_2(self):
        self._create({
            "directory"       : "metadata////",
            "extension-format": "json",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}metadata/file.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_directory_format(self):
        self._create(
            {"directory": ["..", "json", "\fE str(id // 500 * 500 + 500)"]},
            {"id": 12345},
        )

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}../json/12500/file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_directory_empty(self):
        self._create(
            {"directory": []},
        )

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}./file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_basedirectory(self):
        self._create({"base-directory": True})

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.basedirectory}file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_basedirectory_custom(self):
        self._create({
            "base-directory": "/home/test",
            "directory": "meta",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = "/home/test/meta/file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_filename(self):
        self._create({
            "filename"        : "{category}_{filename}_/meta/\n\r.data",
            "extension-format": "json",
        })

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        path = f"{self.pathfmt.realdirectory}test_file__meta_.data"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_meta_path(self):
        self._create({
            "metadata-path": "_meta_path",
        })

        self._trigger()

        self.assertEqual(self.pathfmt.kwdict["_meta_path"],
                         f"{self.pathfmt.realpath}.json")

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

        path = f"{self.pathfmt.realdirectory}file.ext.json"
        m.assert_called_once_with(path, "w", encoding="utf-8", newline=None)

    def test_metadata_option_skip_false(self):
        self._create({"skip": False})

        with patch("builtins.open", mock_open()) as m, \
                patch("os.path.exists") as e:
            self._trigger()

        self.assertTrue(not e.called)
        self.assertTrue(m.called)

    def test_metadata_option_newline(self):
        self._create({
            "newline": "\r\n",
            "filename"      : "data.json",
            "directory"     : "",
            "base-directory": self.dir.name,
        })

        self._trigger()

        path = os.path.join(self.dir.name, "data.json")
        with open(path, newline="") as fp:
            content = fp.read()

        self.assertEqual(content, """\
{\r\n\
    "category": "test",\r\n\
    "filename": "file",\r\n\
    "extension": "ext"\r\n\
}\r\n\
""")

    def test_metadata_option_include(self):
        self._create(
            {"include": ["_private", "filename", "foo"], "sort": True},
            {"public": "hello ワールド", "_private": "foo バー"},
        )

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        self.assertEqual(self._output(m), """{
    "_private": "foo バー",
    "filename": "file"
}
""")

    def test_metadata_option_exclude(self):
        self._create(
            {"exclude": ["category", "filename", "foo"], "sort": True},
            {"public": "hello ワールド", "_private": "foo バー"},
        )

        with patch("builtins.open", mock_open()) as m:
            self._trigger()

        self.assertEqual(self._output(m), """{
    "extension": "ext",
    "public": "hello ワールド"
}
""")

    def test_archive(self):
        pp = self._create({
            "archive": ":memory:",
            "event"  : "finalize",
        })

        self.assertIsInstance(pp.archive, archive.DownloadArchive)

        with patch.object(pp.archive, "add") as m_aa, \
                patch.object(pp.archive, "close") as m_ac:
            self._trigger(("finalize",))
        pp.archive.close()

        m_aa.assert_called_once_with(self.pathfmt.kwdict)
        m_ac.assert_called_once()

    def _output(self, mock):
        return "".join(
            call[1][0]
            for call in mock.mock_calls
            if call[0].endswith("write")
        )


class MtimeTest(BasePostprocessorTest):

    def test_mtime_datetime(self):
        self._create(None, {"date": datetime(1980, 1, 1)})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime_meta"], 315532800)

    def test_mtime_timestamp(self):
        self._create(None, {"date": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime_meta"], 315532800)

    def test_mtime_none(self):
        self._create(None, {"date": None})
        self._trigger()
        self.assertNotIn("_mtime_meta", self.pathfmt.kwdict)

    def test_mtime_undefined(self):
        self._create(None, {})
        self._trigger()
        self.assertNotIn("_mtime_meta", self.pathfmt.kwdict)

    def test_mtime_key(self):
        self._create({"key": "foo"}, {"foo": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime_meta"], 315532800)

    def test_mtime_value(self):
        self._create({"value": "{foo}"}, {"foo": 315532800})
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_mtime_meta"], 315532800)


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

        self._create({"function": f"{path}:calc"}, {"_value": 12})

        self.assertNotIn("_result", self.pathfmt.kwdict)
        self._trigger()
        self.assertEqual(self.pathfmt.kwdict["_result"], 24)

    def test_eval(self):
        self._create({"mode": "eval", "expression": "abort()"})

        with self.assertRaises(exception.StopExtraction):
            self._trigger()

    def test_eval_auto(self):
        self._create({"expression": "abort()"})

        with self.assertRaises(exception.StopExtraction):
            self._trigger()

    def test_archive(self):
        pp = self._create({
            "expression": "True",
            "archive"   : ":memory:",
            "event"     : "finalize",
        })

        self.assertIsInstance(pp.archive, archive.DownloadArchive)

        with patch.object(pp.archive, "add") as m_aa, \
                patch.object(pp.archive, "close") as m_ac:
            self._trigger(("finalize",))
        pp.archive.close()

        m_aa.assert_called_once_with(self.pathfmt.kwdict)
        m_ac.assert_called_once()

    def _write_module(self, path):
        with open(path, "w") as fp:
            fp.write("""
def calc(kwdict):
    kwdict["_result"] = kwdict["_value"] * 2
""")


class RenameTest(BasePostprocessorTest):

    def _prepare(self, filename):
        path = self.pathfmt.realdirectory
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)

        with open(path + filename, "w"):
            pass

        return path

    def test_rename_from(self):
        self._create({"from": "{id}.{extension}"}, {"id": 12345})
        path = self._prepare("12345.ext")

        self._trigger()

        self.assertEqual(os.listdir(path), ["file.ext"])

    def test_rename_to(self):
        self._create({"to": "{id}.{extension}"}, {"id": 12345})
        path = self._prepare("file.ext")

        self._trigger(("skip",))

        self.assertEqual(os.listdir(path), ["12345.ext"])

    def test_rename_from_to(self):
        self._create({"from": "name", "to": "{id}"}, {"id": 12345})
        path = self._prepare("name")

        self._trigger()

        self.assertEqual(os.listdir(path), ["12345"])

    def test_rename_noopt(self):
        with self.assertRaises(ValueError):
            self._create({})

    def test_rename_skip(self):
        self._create({"from": "{id}.{extension}"}, {"id": 12345})
        path = self._prepare("12345.ext")
        with open(f"{path}file.ext", "w"):
            pass

        with self.assertLogs("postprocessor.rename", level="WARNING") as cm:
            self._trigger()
        self.assertTrue(cm.output[0].startswith(
            "WARNING:postprocessor.rename:Not renaming "
            "'12345.ext' to 'file.ext'"))
        self.assertEqual(sorted(os.listdir(path)), ["12345.ext", "file.ext"])


class ZipTest(BasePostprocessorTest):

    def test_zip_default(self):
        pp = self._create()
        self.assertEqual(self.job.hooks["file"][0], pp.write_fast)
        self.assertEqual(pp.path, self.pathfmt.realdirectory[:-1])
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            f"{pp.path}.zip", "a", zipfile.ZIP_STORED, True,
        ))
        self.assertTrue(pp.args[0].endswith("/test.zip"))

    def test_zip_safe(self):
        pp = self._create({"mode": "safe"})
        self.assertEqual(self.job.hooks["file"][0], pp.write_safe)
        self.assertEqual(pp.path, self.pathfmt.realdirectory[:-1])
        self.assertEqual(pp.delete, True)
        self.assertEqual(pp.args, (
            f"{pp.path}.zip", "a", zipfile.ZIP_STORED, True,
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
            f"{pp.path}.cbz", "a", zipfile.ZIP_DEFLATED, True,
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
                name = f"file{i}.ext"
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
            self.pathfmt.temppath = f"{self.pathfmt.realdirectory}file.ext"
            self.pathfmt.filename = f"file{i}.ext"
            self._trigger()

        # write the last file a second time (should be skipped)
        self._trigger()

        # close file
        self._trigger(("finalize",))

        self.assertEqual(pp.zfile.write.call_count, 3)
        for call_args in pp.zfile.write.call_args_list:
            args, kwargs = call_args
            self.assertEqual(len(args), 2)
            self.assertEqual(len(kwargs), 0)
            self.assertEqual(args[0], self.pathfmt.temppath)
            self.assertRegex(args[1], r"file\d\.ext")
        self.assertEqual(pp.zfile.close.call_count, 1)


if __name__ == "__main__":
    unittest.main()
