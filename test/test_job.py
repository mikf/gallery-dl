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


class TestDataJob(unittest.TestCase):

    def test_default(self):
        pass


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
                "tags": ["foo", "bar"],
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


if __name__ == '__main__':
    unittest.main()
