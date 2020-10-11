#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, util, job, config, exception  # noqa E402


# these don't work on Travis CI
TRAVIS_SKIP = {
    "exhentai", "mangafox", "dynastyscans", "nijie", "instagram", "ngomik",
    "archivedmoe", "archiveofsins", "thebarchive", "fireden", "4plebs",
    "sankaku", "idolcomplex", "mangahere", "mangadex", "sankakucomplex",
    "warosu", "fuskator", "patreon", "komikcast",
}

# temporary issues, etc.
BROKEN = {
    "imagevenue",
    "ngomik",
    "photobucket",
}


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

    def _run_test(self, extr, url, result):
        if result:
            if "options" in result:
                for key, value in result["options"]:
                    key = key.split(".")
                    config.set(key[:-1], key[-1], value)
            if "range" in result:
                config.set((), "image-range"  , result["range"])
                config.set((), "chapter-range", result["range"])
            content = "content" in result
        else:
            content = False

        tjob = ResultJob(url, content=content)
        self.assertEqual(extr, tjob.extractor.__class__)

        if not result:
            return
        if "exception" in result:
            with self.assertRaises(result["exception"]):
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
                self._skipped.append((url, exc))
                self.skipTest(exc)
            raise

        if result.get("archive", True):
            self.assertEqual(
                len(set(tjob.archive_list)),
                len(tjob.archive_list),
                "archive-id uniqueness",
            )

        if tjob.queue:
            # test '_extractor' entries
            for url, kwdict in zip(tjob.url_list, tjob.kwdict_list):
                if "_extractor" in kwdict:
                    extr = kwdict["_extractor"].from_url(url)
                    self.assertIsInstance(extr, kwdict["_extractor"])
                    self.assertEqual(extr.url, url)
        else:
            # test 'extension' entries
            for kwdict in tjob.kwdict_list:
                self.assertIn("extension", kwdict)

        # test extraction results
        if "url" in result:
            self.assertEqual(result["url"], tjob.url_hash.hexdigest())

        if "content" in result:
            expected = result["content"]
            digest = tjob.content_hash.hexdigest()
            if isinstance(expected, str):
                self.assertEqual(digest, expected, "content")
            else:  # assume iterable
                self.assertIn(digest, expected, "content")

        if "keyword" in result:
            expected = result["keyword"]
            if isinstance(expected, dict):
                for kwdict in tjob.kwdict_list:
                    self._test_kwdict(kwdict, expected)
            else:  # assume SHA1 hash
                self.assertEqual(expected, tjob.kwdict_hash.hexdigest())

        if "count" in result:
            count = result["count"]
            if isinstance(count, str):
                self.assertRegex(count, r"^ *(==|!=|<|<=|>|>=) *\d+ *$")
                expr = "{} {}".format(len(tjob.url_list), count)
                self.assertTrue(eval(expr), msg=expr)
            else:  # assume integer
                self.assertEqual(len(tjob.url_list), count)

        if "pattern" in result:
            self.assertGreater(len(tjob.url_list), 0)
            for url in tjob.url_list:
                self.assertRegex(url, result["pattern"])

    def _test_kwdict(self, kwdict, tests):
        for key, test in tests.items():
            if key.startswith("?"):
                key = key[1:]
                if key not in kwdict:
                    continue
            self.assertIn(key, kwdict)
            value = kwdict[key]

            if isinstance(test, dict):
                self._test_kwdict(value, test)
            elif isinstance(test, type):
                self.assertIsInstance(value, test, msg=key)
            elif isinstance(test, str):
                if test.startswith("re:"):
                    self.assertRegex(value, test[3:], msg=key)
                elif test.startswith("dt:"):
                    self.assertIsInstance(value, datetime.datetime, msg=key)
                    self.assertEqual(str(value), test[3:], msg=key)
                elif test.startswith("type:"):
                    self.assertEqual(type(value).__name__, test[5:], msg=key)
                else:
                    self.assertEqual(value, test, msg=key)
            else:
                self.assertEqual(value, test, msg=key)


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

        self.format_directory = TestFormatter(
            "".join(self.extractor.directory_fmt)).format_map
        self.format_filename = TestFormatter(
            self.extractor.filename_fmt).format_map

    def run(self):
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
        archive_id = self.extractor.archive_fmt.format_map(kwdict)
        self.archive_list.append(archive_id)
        self.archive_hash.update(archive_id.encode())

    def _update_content(self, url, kwdict):
        if self.content:
            scheme = url.partition(":")[0]
            self.fileobj.kwdict = kwdict
            self.get_downloader(scheme).download(url, self.fileobj)


class TestPathfmt():

    def __init__(self, hashobj):
        self.hashobj = hashobj
        self.path = ""
        self.size = 0
        self.kwdict = {}
        self.extension = "jpg"

    def __enter__(self):
        return self

    def __exit__(self, *args):
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


class TestFormatter(util.Formatter):

    @staticmethod
    def _noop(_):
        return ""

    def _apply_simple(self, key, fmt):
        if key == "extension" or "._parse_optional." in repr(fmt):
            return self._noop

        def wrap(obj):
            return fmt(obj[key])
        return wrap

    def _apply(self, key, funcs, fmt):
        if key == "extension" or "._parse_optional." in repr(fmt):
            return self._noop

        def wrap(obj):
            obj = obj[key]
            for func in funcs:
                obj = func(obj)
            return fmt(obj)
        return wrap


def setup_test_config():
    name = "gallerydl"
    email = "gallerydl@openaliasbox.org"

    config.clear()
    config.set(("cache",), "file", None)
    config.set(("downloader",), "part", False)
    config.set(("downloader",), "adjust-extensions", False)
    config.set(("extractor" ,), "timeout" , 60)
    config.set(("extractor" ,), "username", name)
    config.set(("extractor" ,), "password", name)

    config.set(("extractor", "nijie")     , "username", email)
    config.set(("extractor", "seiga")     , "username", email)

    config.set(("extractor", "newgrounds"), "username", "d1618111")
    config.set(("extractor", "newgrounds"), "password", "d1618111")

    config.set(("extractor", "mangoxo")   , "username", "LiQiang3")
    config.set(("extractor", "mangoxo")   , "password", "5zbQF10_5u25259Ma")

    for category in ("danbooru", "instagram", "twitter", "subscribestar",
                     "e621", "inkbunny"):
        config.set(("extractor", category), "username", None)

    config.set(("extractor", "mastodon.social"), "access-token",
               "Blf9gVqG7GytDTfVMiyYQjwVMQaNACgf3Ds3IxxVDUQ")

    config.set(("extractor", "deviantart"), "client-id", "7777")
    config.set(("extractor", "deviantart"), "client-secret",
               "ff14994c744d9208e5caeec7aab4a026")

    config.set(("extractor", "tumblr"), "api-key",
               "0cXoHfIqVzMQcc3HESZSNsVlulGxEXGDTTZCDrRrjaa0jmuTc6")
    config.set(("extractor", "tumblr"), "api-secret",
               "6wxAK2HwrXdedn7VIoZWxGqVhZ8JdYKDLjiQjL46MLqGuEtyVj")
    config.set(("extractor", "tumblr"), "access-token",
               "N613fPV6tOZQnyn0ERTuoEZn0mEqG8m2K8M3ClSJdEHZJuqFdG")
    config.set(("extractor", "tumblr"), "access-token-secret",
               "sgOA7ZTT4FBXdOGGVV331sSp0jHYp4yMDRslbhaQf7CaS71i4O")


def generate_tests():
    """Dynamically generate extractor unittests"""
    def _generate_test(extr, tcase):
        def test(self):
            url, result = tcase
            print("\n", url, sep="")
            self._run_test(extr, url, result)
        return test

    # enable selective testing for direct calls
    if __name__ == '__main__' and len(sys.argv) > 1:
        if sys.argv[1].lower() == "all":
            fltr = lambda c, bc: True  # noqa: E731
        elif sys.argv[1].lower() == "broken":
            fltr = lambda c, bc: c in BROKEN  # noqa: E731
        else:
            argv = sys.argv[1:]
            fltr = lambda c, bc: c in argv or bc in argv  # noqa: E731
        del sys.argv[1:]
    else:
        skip = set(BROKEN)
        if "CI" in os.environ and "TRAVIS" in os.environ:
            skip |= set(TRAVIS_SKIP)
        if skip:
            print("skipping:", ", ".join(skip))
        fltr = lambda c, bc: c not in skip  # noqa: E731

    # filter available extractor classes
    extractors = [
        extr for extr in extractor.extractors()
        if fltr(extr.category, getattr(extr, "basecategory", None))
    ]

    # add 'test_...' methods
    for extr in extractors:
        name = "test_" + extr.__name__ + "_"
        for num, tcase in enumerate(extr._get_tests(), 1):
            test = _generate_test(extr, tcase)
            test.__name__ = name + str(num)
            setattr(TestExtractorResults, test.__name__, test)


generate_tests()
if __name__ == '__main__':
    unittest.main(warnings='ignore')
