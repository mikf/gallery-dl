#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import patch

import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import job, config, text  # noqa E402
from gallery_dl.extractor.common import Extractor, Message  # noqa E402


class TestJob(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def _capture_stdout(self, extr_or_job):
        if isinstance(extr_or_job, Extractor):
            jobinstance = self.jobclass(extr_or_job)
        else:
            jobinstance = extr_or_job

        with io.StringIO() as buffer:
            stdout = sys.stdout
            sys.stdout = buffer
            try:
                jobinstance.run()
            finally:
                sys.stdout = stdout

            return buffer.getvalue()


class TestDownloadJob(TestJob):
    jobclass = job.DownloadJob

    def test_extractor_filter(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr)

        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorNoop)  , True)

        config.set((), "blacklist", ":test_subcategory")
        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorNoop)  , False)

        config.set((), "whitelist", "test_category:test_subcategory")
        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , True)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorNoop)  , False)

    def test_opt_init(self):
        config.set((), "init", True)
        config.set((), "archive", ":memory:")
        config.set((), "postprocessors", "directory")

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()

        self.assertTrue(tjob.pathfmt)
        self.assertTrue(tjob.archive)
        self.assertTrue(tjob.hooks)

    def test_opt_init_false(self):
        config.set((), "init", False)
        config.set((), "archive", ":memory:")
        config.set((), "postprocessors", "directory")

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()

        self.assertFalse(tjob.pathfmt)
        self.assertFalse(tjob.archive)
        self.assertFalse(tjob.hooks)

    def test_parent_metadata_extractor(self):
        config.set((), "parent-metadata", True)

        config.set(("output",), "mode", False)
        config.set((), "download", False)

        config.set((), "postprocessors", [{
            "name"  : "metadata/print@init",
            "format": "{num}",
        }])

        extr = TestExtractorParent.from_url("test:parent:3")
        out = self._capture_stdout(extr)
        # no output if '_extractor' is overwritten (#8958)
        self.assertEqual(out, "11\n")


class TestKeywordJob(TestJob):
    jobclass = job.KeywordJob

    def test_default(self):
        self.maxDiff = None
        extr = TestExtractor.from_url("test:self")
        self.assertEqual(self._capture_stdout(extr), """\
Keywords for directory names:
-----------------------------
author['id']
  123
author['name']
  test
author['self']
  <circular reference>
category
  test_category
subcategory
  test_subcategory
user['id']
  123
user['name']
  test
user['self']
  <circular reference>

Keywords for filenames and --filter:
------------------------------------
author['id']
  123
author['name']
  test
author['self']
  <circular reference>
category
  test_category
extension
  jpg
filename
  1
num
  1
subcategory
  test_subcategory
tags[N]
  0 foo
  1 bar
  2 テスト
user['id']
  123
user['name']
  test
user['self']
  <circular reference>
""")

    def test_opt_init(self):
        config.set((), "init", True)

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()


class TestUrlJob(TestJob):
    jobclass = job.UrlJob

    def test_default(self):
        extr = TestExtractor.from_url("test:")
        self.assertEqual(self._capture_stdout(extr), """\
https://example.org/1.jpg
https://example.org/2.jpg
https://example.org/3.jpg
""")

    def test_fallback(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr)
        tjob.handle_url = tjob.handle_url_fallback

        self.assertEqual(self._capture_stdout(tjob), """\
https://example.org/1.jpg
| https://example.org/alt/1.jpg
https://example.org/2.jpg
| https://example.org/alt/2.jpg
https://example.org/3.jpg
| https://example.org/alt/3.jpg
""")

    def test_parent(self):
        extr = TestExtractorParent.from_url("test:parent")
        self.assertEqual(self._capture_stdout(extr), """\
test:child
test:child
test:child
""")

    def test_child(self):
        extr = TestExtractorParent.from_url("test:parent")
        tjob = self.jobclass(extr, depth=0)
        self.assertEqual(self._capture_stdout(tjob), 3 * """\
https://example.org/1.jpg
https://example.org/2.jpg
https://example.org/3.jpg
""")

    def test_opt_init(self):
        config.set((), "init", True)

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()

    def test_opt_follow(self):
        config.set((), "follow", "{user[bio]}")

        extr = TestExtractor.from_url("test:urls")
        tjob = self.jobclass(extr)
        self.assertEqual(self._capture_stdout(tjob), """\
https://example.org/1.jpg
https://example.org/2.jpg
https://example.org/3.jpg
https://example1.org/content/abc
https://example2.org/content?query=123
https://example3.org/content/#frag
""")


class TestInfoJob(TestJob):
    jobclass = job.InfoJob

    def test_default(self):
        extr = TestExtractor.from_url("test:")
        self.assertEqual(self._capture_stdout(extr), """\
Category / Subcategory
  "test_category" / "test_subcategory"

Filename format (default):
  "test_{filename}.{extension}"

Directory format (default):
  ["{category}"]

""")

    def test_custom(self):
        config.set((), "filename", "custom")
        config.set((), "directory", ("custom",))
        config.set((), "sleep-request", 321)
        extr = TestExtractor.from_url("test:")
        extr.request_interval = 123.456

        self.assertEqual(self._capture_stdout(extr), """\
Category / Subcategory
  "test_category" / "test_subcategory"

Filename format (custom):
  "custom"
Filename format (default):
  "test_{filename}.{extension}"

Directory format (custom):
  ["custom"]
Directory format (default):
  ["{category}"]

Request interval (custom):
  321
Request interval (default):
  123.456

""")

    def test_base_category(self):
        extr = TestExtractor.from_url("test:")
        extr.basecategory = "test_basecategory"
        extr.basesubcategory = "test_basesubcategory"

        self.assertEqual(self._capture_stdout(extr), """\
Category / Subcategory / Basecategory
  "test_category" / "test_subcategory" / "test_basecategory"

Filename format (default):
  "test_{filename}.{extension}"

Directory format (default):
  ["{category}"]

""")

    def test_opt_init(self):
        config.set((), "init", True)

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()


class TestDataJob(TestJob):
    jobclass = job.DataJob

    def test_default(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())
        user = {"id": 123, "name": "test"}

        tjob.run()

        self.assertEqual(tjob.data, [
            (Message.Directory, {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "user"       : user,
                "author"     : user,
            }),
            (Message.Url, "https://example.org/1.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "1",
                "extension"  : "jpg",
                "num"        : 1,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : user,
                "author"     : user,
            }),
            (Message.Url, "https://example.org/2.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "2",
                "extension"  : "jpg",
                "num"        : 2,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : user,
                "author"     : user,
            }),
            (Message.Url, "https://example.org/3.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "3",
                "extension"  : "jpg",
                "num"        : 3,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : user,
                "author"     : user,
            }),
        ])

    def test_exception(self):
        extr = TestExtractorException.from_url("test:exception")
        tjob = self.jobclass(extr, file=io.StringIO())
        tjob.run()
        self.assertEqual(
            tjob.data[-1],
            (-1, {
                "error"  : "ZeroDivisionError",
                "message": "division by zero",
            })
        )

    def test_private(self):
        config.set(("output",), "private", True)
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())

        tjob.run()

        for i in range(1, 4):
            self.assertEqual(
                tjob.data[i][2]["_fallback"],
                (f"https://example.org/alt/{i}.jpg",),
            )

    def test_sleep(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())

        config.set((), "sleep-extractor", 123)
        with patch("time.sleep") as sleep:
            tjob.run()
        sleep.assert_called_once_with(123)

        config.set((), "sleep-extractor", 0)
        with patch("time.sleep") as sleep:
            tjob.run()
        sleep.assert_not_called()

    def test_ascii(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr)

        tjob.file = buffer = io.StringIO()
        tjob.run()
        self.assertIn("""\
      "tags": [
        "foo",
        "bar",
        "\\u30c6\\u30b9\\u30c8"
      ],
""", buffer.getvalue())

        tjob.file = buffer = io.StringIO()
        tjob.ascii = False
        tjob.run()
        self.assertIn("""\
      "tags": [
        "foo",
        "bar",
        "テスト"
      ],
""", buffer.getvalue())

    def test_num_string(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())

        with patch("gallery_dl.util.number_to_string") as nts:
            tjob.run()
        self.assertEqual(len(nts.call_args_list), 0)

        config.set(("output",), "num-to-str", True)
        with patch("gallery_dl.util.number_to_string") as nts:
            tjob.run()
        self.assertEqual(len(nts.call_args_list), 72)

        tjob.run()
        self.assertEqual(tjob.data[-1][0], Message.Url)
        self.assertEqual(tjob.data[-1][2]["num"], "3")

    def test_jsonl(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())
        with patch("gallery_dl.job.DataJob.out") as out:
            tjob.run()
        self.assertEqual(len(out.call_args_list), 0)

        config.set(("output",), "jsonl", True)
        extr = TestExtractor.from_url("test:")
        file = io.StringIO()
        tjob = self.jobclass(extr, file=file)
        with patch("gallery_dl.job.DataJob.out") as out:
            tjob.run()
        self.assertEqual(len(out.call_args_list), 4)

        tjob.run()
        for line in file.getvalue().split():
            self.assertRegex(line, r"""^\[[23],("http[^"]+",)?\{.+\}\]$""")

    def test_opt_init(self):
        config.set((), "init", True)

        extr = TestExtractorNoop.from_url("test:noop")
        tjob = self.jobclass(extr)
        tjob._init()

    def test_opt_follow(self):
        config.set((), "follow", "{user[bio]!R}")

        extr = TestExtractor.from_url("test:urls")
        tjob = self.jobclass(extr, file=None)
        tjob.run()
        self.assertEqual(tjob.data_urls, [
            "https://example.org/1.jpg",
            "https://example.org/2.jpg",
            "https://example.org/3.jpg",
            "https://example1.org/content/abc",
            "https://example2.org/content?query=123",
            "https://example3.org/content/#frag"
        ])

    def test_resolve(self):
        extr = TestExtractorParent.from_url("test:parent:3")
        tjob = self.jobclass(extr, file=None, resolve=0)
        tjob.run()
        self.assertEqual(len(tjob.data_urls), 3)
        for url in tjob.data_urls:
            self.assertEqual(url, "test:parent:2")

        extr = TestExtractorParent.from_url("test:parent:3")
        tjob = self.jobclass(extr, file=None, resolve=1)
        tjob.run()
        self.assertEqual(len(tjob.data_urls), 9)
        for url in tjob.data_urls:
            self.assertEqual(url, "test:parent:1")

        extr = TestExtractorParent.from_url("test:parent")
        tjob = self.jobclass(extr, file=None, resolve=64)
        tjob.run()
        self.assertEqual(len(tjob.data_urls), 9)
        for url in tjob.data_urls:
            self.assertRegex(url, r"^https://example.org/\d\.jpg$")

        extr = TestExtractorParent.from_url("test:parent:1")
        tjob = self.jobclass(extr, file=None, resolve=64)
        tjob.run()
        self.assertEqual(len(tjob.data_urls), 27)

        extr = TestExtractorParent.from_url("test:parent:2")
        tjob = self.jobclass(extr, file=None, resolve=64)
        tjob.run()
        self.assertEqual(len(tjob.data_urls), 81)


class TestExtractor(Extractor):
    category = "test_category"
    subcategory = "test_subcategory"
    directory_fmt = ("{category}",)
    filename_fmt = "test_{filename}.{extension}"
    pattern = r"test:(child|self|urls)?$"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = {"id": 123, "name": "test"}
        if match[1] == "self":
            self.user["self"] = self.user
        elif match[1] == "urls":
            self.user["bio"] = """
Site 1:
* https://example1.org/content/abc
Site 2:
* https://example2.org/content?query=123

<a href="https://example3.org/content/#frag">Site 3</a>
"""

    def items(self):
        root = "https://example.org"
        user = self.user

        yield Message.Directory, "", {
            "user": user,
            "author": user,
        }

        for i in range(1, 4):
            url = f"{root}/{i}.jpg"
            yield Message.Url, url, text.nameext_from_url(url, {
                "num" : i,
                "tags": ["foo", "bar", "テスト"],
                "user": user,
                "author": user,
                "_fallback": (f"{root}/alt/{i}.jpg",),
            })


class TestExtractorParent(Extractor):
    category = "test_category"
    subcategory = "test_subcategory_parent"
    pattern = r"test:parent(:\d+)?"

    def items(self):
        level = self.groups[0]
        if level in {None, ":0"}:
            url = "test:child"
            extr = TestExtractor
        else:
            url = f"test:parent:{int(level[1:])-1}"
            extr = TestExtractorParent

        for i in range(11, 14):
            yield Message.Queue, url, {
                "num" : i,
                "tags": ["abc", "def"],
                "_extractor": extr,
            }


class TestExtractorException(Extractor):
    category = "test_category"
    subcategory = "test_subcategory_exception"
    pattern = r"test:exception$"

    def items(self):
        return 1/0


class TestExtractorNoop(Extractor):
    category = "test_category_alt"
    subcategory = "test_subcategory"
    pattern = r"test:noop"


if __name__ == "__main__":
    unittest.main()
