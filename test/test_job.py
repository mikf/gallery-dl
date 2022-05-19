#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import patch

import io
import contextlib

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
            with contextlib.redirect_stdout(buffer):
                jobinstance.run()
            return buffer.getvalue()


class TestDownloadJob(TestJob):
    jobclass = job.DownloadJob

    def test_extractor_filter(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr)

        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , True)

        config.set((), "blacklist", ":test_subcategory")
        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , False)
        self.assertEqual(func(TestExtractorParent), True)
        self.assertEqual(func(TestExtractorAlt)   , False)

        config.set((), "whitelist", "test_category:test_subcategory")
        func = tjob._build_extractor_filter()
        self.assertEqual(func(TestExtractor)      , True)
        self.assertEqual(func(TestExtractorParent), False)
        self.assertEqual(func(TestExtractorAlt)   , False)


class TestKeywordJob(TestJob):
    jobclass = job.KeywordJob

    def test_default(self):
        extr = TestExtractor.from_url("test:")
        self.assertEqual(self._capture_stdout(extr), """\
Keywords for directory names:
-----------------------------
category
  test_category
subcategory
  test_subcategory

Keywords for filenames and --filter:
------------------------------------
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
tags[]
  - foo
  - bar
  - テスト
user[id]
  123
user[name]
  test
""")


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
        tjob = job.UrlJob(extr, depth=0)
        self.assertEqual(self._capture_stdout(tjob), 3 * """\
https://example.org/1.jpg
https://example.org/2.jpg
https://example.org/3.jpg
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

        self.assertEqual(self._capture_stdout(extr), """\
Category / Subcategory / Basecategory
  "test_category" / "test_subcategory" / "test_basecategory"

Filename format (default):
  "test_{filename}.{extension}"

Directory format (default):
  ["{category}"]

""")


class TestDataJob(TestJob):
    jobclass = job.DataJob

    def test_default(self):
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())

        tjob.run()

        self.assertEqual(tjob.data, [
            (Message.Directory, {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
            }),
            (Message.Url, "https://example.org/1.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "1",
                "extension"  : "jpg",
                "num"        : 1,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : {"id": 123, "name": "test"},
            }),
            (Message.Url, "https://example.org/2.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "2",
                "extension"  : "jpg",
                "num"        : 2,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : {"id": 123, "name": "test"},
            }),
            (Message.Url, "https://example.org/3.jpg", {
                "category"   : "test_category",
                "subcategory": "test_subcategory",
                "filename"   : "3",
                "extension"  : "jpg",
                "num"        : 3,
                "tags"       : ["foo", "bar", "テスト"],
                "user"       : {"id": 123, "name": "test"},
            }),
        ])

    def test_exception(self):
        extr = TestExtractorException.from_url("test:exception")
        tjob = self.jobclass(extr, file=io.StringIO())
        tjob.run()
        self.assertEqual(
            tjob.data[-1], ("ZeroDivisionError", "division by zero"))

    def test_private(self):
        config.set(("output",), "private", True)
        extr = TestExtractor.from_url("test:")
        tjob = self.jobclass(extr, file=io.StringIO())

        tjob.run()

        for i in range(1, 4):
            self.assertEqual(
                tjob.data[i][2]["_fallback"],
                ("https://example.org/alt/{}.jpg".format(i),),
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
        self.assertEqual(len(nts.call_args_list), 52)

        tjob.run()
        self.assertEqual(tjob.data[-1][0], Message.Url)
        self.assertEqual(tjob.data[-1][2]["num"], "3")


class TestExtractor(Extractor):
    category = "test_category"
    subcategory = "test_subcategory"
    directory_fmt = ("{category}",)
    filename_fmt = "test_{filename}.{extension}"
    pattern = r"test:(child)?$"

    def items(self):
        root = "https://example.org"

        yield Message.Directory, {}
        for i in range(1, 4):
            url = "{}/{}.jpg".format(root, i)
            yield Message.Url, url, text.nameext_from_url(url, {
                "num" : i,
                "tags": ["foo", "bar", "テスト"],
                "user": {"id": 123, "name": "test"},
                "_fallback": ("{}/alt/{}.jpg".format(root, i),),
            })


class TestExtractorParent(Extractor):
    category = "test_category"
    subcategory = "test_subcategory_parent"
    pattern = r"test:parent"

    def items(self):
        url = "test:child"

        for i in range(11, 14):
            yield Message.Queue, url, {
                "num" : i,
                "tags": ["abc", "def"],
                "_extractor": TestExtractor,
            }


class TestExtractorException(Extractor):
    category = "test_category"
    subcategory = "test_subcategory_exception"
    pattern = r"test:exception$"

    def items(self):
        return 1/0


class TestExtractorAlt(Extractor):
    category = "test_category_alt"
    subcategory = "test_subcategory"


if __name__ == '__main__':
    unittest.main()
