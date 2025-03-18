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

import re
import json
import hashlib
import datetime
import collections

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import \
    extractor, util, job, config, exception, formatter  # noqa E402


RESULTS = os.environ.get("GDL_TEST_RESULTS")
if RESULTS:
    results = util.import_file(RESULTS)
else:
    from test import results


# temporary issues, etc.
BROKEN = {
}

CONFIG = {
    "cache": {
        "file": None,
    },
    "downloader": {
        "adjust-extensions": False,
        "part": False,
    },
}


AUTH_REQUIRED = {
    "pixiv",
    "nijie",
    "horne",
    "reddit",
    "seiga",
    "fantia",
    "instagram",
    "twitter",
}

AUTH_KEYS = (
    "username",
    "cookies",
    "api-key",
    "client-id",
    "access-token",
    "refresh-token",
)


class TestExtractorResults(unittest.TestCase):

    def setUp(self):
        setup_test_config()

    def tearDown(self):
        config.clear()

    @classmethod
    def setUpClass(cls):
        cls._skipped = []

    @classmethod
    def tearDownClass(cls):
        if cls._skipped:
            print("\n\nSkipped tests:")
            for url, exc in cls._skipped:
                print('- {} ("{}")'.format(url, exc))

    def assertRange(self, value, range, msg=None):
        if range.step > 1:
            self.assertIn(value, range, msg=msg)
        else:
            self.assertLessEqual(value, range.stop, msg=msg)
            self.assertGreaterEqual(value, range.start, msg=msg)

    def _run_test(self, result):
        if result.get("#fail"):
            del result["#fail"]
            try:
                self._run_test(result)
            except AssertionError:
                return
            else:
                self.fail("Test did not fail")

        base, cat, sub = result_categories(result)
        result.pop("#comment", None)
        result.pop("#category", None)
        auth = result.pop("#auth", None)

        extr_url = extractor.find(result["#url"])
        self.assertTrue(extr_url, "extractor by URL/find")
        extr_cls = extr = result["#class"].from_url(result["#url"])
        self.assertTrue(extr_url, "extractor by cls.from_url()")
        self.assertIs(extr_url.__class__, extr_cls.__class__)

        if len(result) <= 2:
            return  # only matching

        skip = result.pop("#skip", False)
        if skip:
            return self._skipped.append((result["#url"], skip))

        if auth is None:
            auth = (cat in AUTH_REQUIRED)
        elif not auth:
            # auth explicitly disabled
            for key in AUTH_KEYS:
                config.set((), key, None)

        if auth and not any(extr.config(key) for key in AUTH_KEYS):
            return self._skipped.append((result["#url"], "no auth"))

        if "#options" in result:
            for key, value in result["#options"].items():
                key = key.split(".")
                config.set(key[:-1], key[-1], value)
        if "#range" in result:
            config.set((), "image-range"  , result["#range"])
            config.set((), "chapter-range", result["#range"])

        tjob = ResultJob(extr, content=("#sha1_content" in result))

        if "#exception" in result:
            with self.assertRaises(result["#exception"], msg="#exception"):
                tjob.run()
            return

        try:
            tjob.run()
        except exception.StopExtraction:
            pass
        except exception.HttpError as exc:
            exc = str(exc)
            if re.match(r"'5\d\d ", exc) or \
                    re.search(r"\bRead timed out\b", exc):
                self._skipped.append((result["#url"], exc))
                self.skipTest(exc)
            raise

        if result.get("#archive", True):
            self.assertEqual(
                len(set(tjob.archive_list)),
                len(tjob.archive_list),
                msg="archive-id uniqueness")

        if tjob.queue:
            # test '_extractor' entries
            for url, kwdict in zip(tjob.url_list, tjob.kwdict_list):
                if "_extractor" in kwdict:
                    extr = kwdict["_extractor"].from_url(url)
                    if extr is None and not result.get("#extractor", True):
                        continue
                    self.assertIsInstance(extr, kwdict["_extractor"])
                    self.assertEqual(extr.url, url)
        else:
            # test 'extension' entries
            for kwdict in tjob.kwdict_list:
                self.assertIn("extension", kwdict, msg="#extension")

        # test extraction results
        if "#sha1_url" in result:
            self.assertEqual(
                result["#sha1_url"],
                tjob.url_hash.hexdigest(),
                msg="#sha1_url")

        if "#sha1_content" in result:
            expected = result["#sha1_content"]
            digest = tjob.content_hash.hexdigest()
            if isinstance(expected, str):
                self.assertEqual(expected, digest, msg="#sha1_content")
            else:  # iterable
                self.assertIn(digest, expected, msg="#sha1_content")

        if "#sha1_metadata" in result:
            self.assertEqual(
                result["#sha1_metadata"],
                tjob.kwdict_hash.hexdigest(),
                "#sha1_metadata")

        if "#count" in result:
            count = result["#count"]
            len_urls = len(tjob.url_list)
            if isinstance(count, str):
                self.assertRegex(
                    count, r"^ *(==|!=|<|<=|>|>=) *\d+ *$", msg="#count")
                expr = "{} {}".format(len_urls, count)
                self.assertTrue(eval(expr), msg=expr)
            elif isinstance(count, range):
                self.assertRange(len_urls, count, msg="#count")
            else:  # assume integer
                self.assertEqual(len_urls, count, msg="#count")

        if "#pattern" in result:
            self.assertGreater(len(tjob.url_list), 0, msg="#pattern")
            pattern = result["#pattern"]
            if isinstance(pattern, str):
                for url in tjob.url_list:
                    self.assertRegex(url, pattern, msg="#pattern")
            else:
                for url, pat in zip(tjob.url_list, pattern):
                    self.assertRegex(url, pat, msg="#pattern")

        if "#urls" in result:
            expected = result["#urls"]
            if isinstance(expected, str):
                self.assertTrue(tjob.url_list, msg="#urls")
                self.assertEqual(tjob.url_list[0], expected, msg="#urls")
            else:
                self.assertSequenceEqual(tjob.url_list, expected, msg="#urls")

        metadata = {k: v for k, v in result.items() if k[0] != "#"}
        if metadata:
            for kwdict in tjob.kwdict_list:
                self._test_kwdict(kwdict, metadata)

    def _test_kwdict(self, kwdict, tests, parent=None):
        for key, test in tests.items():
            if key.startswith("?"):
                key = key[1:]
                if key not in kwdict:
                    continue
            path = "{}.{}".format(parent, key) if parent else key
            self.assertIn(key, kwdict, msg=path)
            value = kwdict[key]

            if isinstance(test, dict):
                self._test_kwdict(value, test, path)
            elif isinstance(test, type):
                self.assertIsInstance(value, test, msg=path)
            elif isinstance(test, range):
                self.assertRange(value, test, msg=path)
            elif isinstance(test, set):
                try:
                    self.assertIn(value, test, msg=path)
                except AssertionError:
                    self.assertIn(type(value), test, msg=path)
            elif isinstance(test, list):
                subtest = False
                for idx, item in enumerate(test):
                    if isinstance(item, dict):
                        subtest = True
                        subpath = "{}[{}]".format(path, idx)
                        self._test_kwdict(value[idx], item, subpath)
                if not subtest:
                    self.assertEqual(test, value, msg=path)
            elif isinstance(test, str):
                if test.startswith("re:"):
                    self.assertRegex(value, test[3:], msg=path)
                elif test.startswith("dt:"):
                    self.assertIsInstance(value, datetime.datetime, msg=path)
                    self.assertEqual(test[3:], str(value), msg=path)
                elif test.startswith("type:"):
                    self.assertEqual(test[5:], type(value).__name__, msg=path)
                elif test.startswith("len:"):
                    self.assertIsInstance(value, (list, tuple), msg=path)
                    self.assertEqual(int(test[4:]), len(value), msg=path)
                else:
                    self.assertEqual(test, value, msg=path)
            else:
                self.assertEqual(test, value, msg=path)


class ResultJob(job.DownloadJob):
    """Generate test-results for extractor runs"""

    def __init__(self, url, parent=None, content=False):
        job.DownloadJob.__init__(self, url, parent)
        self.queue = False
        self.content = content

        self.url_list = []
        self.url_hash = hashlib.sha1()
        self.kwdict_list = []
        self.kwdict_hash = hashlib.sha1()
        self.archive_list = []
        self.archive_hash = hashlib.sha1()
        self.content_hash = hashlib.sha1()

        if content:
            self.fileobj = TestPathfmt(self.content_hash)
        else:
            self._update_content = lambda url, kwdict: None

        self.format_directory = TestFormatter(
            "".join(self.extractor.directory_fmt)).format_map
        self.format_filename = TestFormatter(
            self.extractor.filename_fmt).format_map
        self.format_archive = TestFormatter(
            self.extractor.archive_fmt).format_map

    def run(self):
        self._init()
        for msg in self.extractor:
            self.dispatch(msg)

    def handle_url(self, url, kwdict, fallback=None):
        self._update_url(url)
        self._update_kwdict(kwdict)
        self._update_archive(kwdict)
        self._update_content(url, kwdict)
        self.format_filename(kwdict)

    def handle_directory(self, kwdict):
        self._update_kwdict(kwdict, False)
        self.format_directory(kwdict)

    def handle_metadata(self, kwdict):
        pass

    def handle_queue(self, url, kwdict):
        self.queue = True
        self._update_url(url)
        self._update_kwdict(kwdict)

    def _update_url(self, url):
        self.url_list.append(url)
        self.url_hash.update(url.encode())

    def _update_kwdict(self, kwdict, to_list=True):
        if to_list:
            self.kwdict_list.append(kwdict.copy())
        kwdict = util.filter_dict(kwdict)
        self.kwdict_hash.update(
            json.dumps(kwdict, sort_keys=True, default=str).encode())

    def _update_archive(self, kwdict):
        archive_id = self.format_archive(kwdict)
        self.archive_list.append(archive_id)
        self.archive_hash.update(archive_id.encode())

    def _update_content(self, url, kwdict):
        self.fileobj.kwdict = kwdict

        downloader = self.get_downloader(url.partition(":")[0])
        if downloader.download(url, self.fileobj):
            return

        for num, url in enumerate(kwdict.get("_fallback") or (), 1):
            self.log.warning("Trying fallback URL #%d", num)
            downloader = self.get_downloader(url.partition(":")[0])
            if downloader.download(url, self.fileobj):
                return


class TestPathfmt():

    def __init__(self, hashobj):
        self.hashobj = hashobj
        self.path = ""
        self.size = 0
        self.kwdict = {}
        self.extension = "jpg"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def open(self, mode):
        self.size = 0
        return self

    def write(self, content):
        """Update SHA1 hash"""
        self.size += len(content)
        self.hashobj.update(content)

    def tell(self):
        return self.size

    def part_size(self):
        return 0


class TestFormatter(formatter.StringFormatter):

    @staticmethod
    def _noop(_):
        return ""

    def _apply_simple(self, key, fmt):
        if key == "extension" or "_parse_optional." in repr(fmt):
            return self._noop

        def wrap(obj):
            return fmt(obj[key])
        return wrap

    def _apply(self, key, funcs, fmt):
        if key == "extension" or "_parse_optional." in repr(fmt):
            return self._noop

        def wrap(obj):
            obj = obj[key]
            for func in funcs:
                obj = func(obj)
            return fmt(obj)
        return wrap


def setup_test_config():
    config._config.update(CONFIG)


def load_test_config():
    try:
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "archive", "config.json")
        with open(path) as fp:
            CONFIG.update(json.loads(fp.read()))
    except FileNotFoundError:
        pass
    except Exception as exc:
        sys.exit("Error when loading {}: {}: {}".format(
            path, exc.__class__.__name__, exc))


def result_categories(result):
    categories = result.get("#category")
    if categories:
        return categories

    cls = result["#class"]
    return cls.basecategory, cls.category, cls.subcategory


def generate_tests():
    """Dynamically generate extractor unittests"""
    def _generate_method(result):
        def test(self):
            print("\n" + result["#url"])
            try:
                self._run_test(result)
            except KeyboardInterrupt as exc:
                v = input("\n[e]xit | [f]ail | [S]kip ? ").strip().lower()
                if v in ("e", "exit"):
                    raise
                if v in ("f", "fail"):
                    self.fail("manual test failure")
                else:
                    self._skipped.append((result["#url"], "manual skip"))
                    self.skipTest(exc)
        return test

    # enable selective testing for direct calls
    if __name__ == "__main__" and len(sys.argv) > 1:
        category, _, subcategory = sys.argv[1].partition(":")
        del sys.argv[1:]

        if category.startswith("+"):
            basecategory = category[1:].lower()
            tests = [t for t in results.all()
                     if result_categories(t)[0].lower() == basecategory]
        else:
            tests = results.category(category)

        if subcategory:
            if subcategory.startswith("+"):
                url = subcategory[1:]
                tests = [t for t in tests if url in t["#url"]]
            elif subcategory.startswith("~"):
                com = subcategory[1:]
                tests = [t for t in tests
                         if "#comment" in t and com in t["#comment"].lower()]
            else:
                tests = [t for t in tests
                         if result_categories(t)[-1] == subcategory]
    else:
        tests = results.all()

    # add 'test_...' methods
    enum = collections.defaultdict(int)
    for result in tests:
        base, cat, sub = result_categories(result)
        name = "{}_{}".format(cat, sub)
        enum[name] += 1

        method = _generate_method(result)
        method.__doc__ = result["#url"]
        method.__name__ = "test_{}_{}".format(name, enum[name])
        setattr(TestExtractorResults, method.__name__, method)


generate_tests()
if __name__ == "__main__":
    load_test_config()
    unittest.main(warnings="ignore")
