#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import patch

import time
import string
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import extractor, util  # noqa E402
from gallery_dl.extractor import mastodon  # noqa E402
from gallery_dl.extractor.common import Extractor, Message  # noqa E402
from gallery_dl.extractor.directlink import DirectlinkExtractor  # noqa E402

_list_classes = extractor._list_classes

try:
    RESULTS = os.environ.get("GDL_TEST_RESULTS")
    if RESULTS:
        results = util.import_file(RESULTS)
    else:
        from test import results
except ImportError:
    results = None


class FakeExtractor(Extractor):
    category = "fake"
    subcategory = "test"
    pattern = "fake:"

    def items(self):
        yield Message.Version, 1
        yield Message.Url, "text:foobar", {}


class TestExtractorModule(unittest.TestCase):
    VALID_URIS = (
        "https://example.org/file.jpg",
        "tumblr:foobar",
        "oauth:flickr",
        "generic:https://example.org/",
        "recursive:https://example.org/document.html",
    )

    def setUp(self):
        extractor._cache.clear()
        extractor._module_iter = extractor._modules_internal()
        extractor._list_classes = _list_classes

    def test_find(self):
        for uri in self.VALID_URIS:
            result = extractor.find(uri)
            self.assertIsInstance(result, Extractor, uri)

        for not_found in ("", "/tmp/file.ext"):
            self.assertIsNone(extractor.find(not_found))

        for invalid in (None, [], {}, 123, b"test:"):
            with self.assertRaises(TypeError):
                extractor.find(invalid)

    def test_add(self):
        uri = "fake:foobar"
        self.assertIsNone(extractor.find(uri))

        extractor.add(FakeExtractor)
        self.assertIsInstance(extractor.find(uri), FakeExtractor)

    def test_add_module(self):
        uri = "fake:foobar"
        self.assertIsNone(extractor.find(uri))

        classes = extractor.add_module(sys.modules[__name__])
        self.assertEqual(len(classes), 1)
        self.assertEqual(classes[0].pattern, FakeExtractor.pattern)
        self.assertEqual(classes[0], FakeExtractor)
        self.assertIsInstance(extractor.find(uri), FakeExtractor)

    def test_from_url(self):
        for uri in self.VALID_URIS:
            cls = extractor.find(uri).__class__
            extr = cls.from_url(uri)
            self.assertIs(type(extr), cls)
            self.assertIsInstance(extr, Extractor)

        for not_found in ("", "/tmp/file.ext"):
            self.assertIsNone(FakeExtractor.from_url(not_found))

        for invalid in (None, [], {}, 123, b"test:"):
            with self.assertRaises(TypeError):
                FakeExtractor.from_url(invalid)

    @unittest.skipIf(not results, "no test data")
    def test_categories(self):
        for result in results.all():
            url = result["#url"]
            cls = result["#class"]
            try:
                extr = cls.from_url(url)
            except ImportError as exc:
                if exc.name in ("youtube_dl", "yt_dlp"):
                    print("Skipping '{}' category checks".format(cls.category))
                    continue
                raise
            self.assertTrue(extr, url)

            categories = result.get("#category")
            if categories:
                base, cat, sub = categories
            else:
                cat = cls.category
                sub = cls.subcategory
                base = cls.basecategory
            self.assertEqual(extr.category, cat, url)
            self.assertEqual(extr.subcategory, sub, url)
            self.assertEqual(extr.basecategory, base, url)

    @unittest.skipIf(not results, "no test data")
    def test_unique_pattern_matches(self):
        # collect testcase URLs
        test_urls = []
        append = test_urls.append

        for result in results.all():
            append((result["#url"], result["#class"]))

        # iterate over all testcase URLs
        for url, extr1 in test_urls:
            matches = []

            # ... and apply all regex patterns to each one
            for extr2 in _list_classes():

                # skip DirectlinkExtractor pattern if it isn't tested
                if extr1 != DirectlinkExtractor and \
                        extr2 == DirectlinkExtractor:
                    continue

                match = extr2.pattern.match(url)
                if match:
                    matches.append((match, extr2))

            # fail if more or less than 1 match happened
            if len(matches) > 1:
                msg = "'{}' gets matched by more than one pattern:".format(url)
                for match, extr in matches:
                    msg += "\n\n- {}:\n{}".format(
                        extr.__name__, match.re.pattern)
                self.fail(msg)

            elif len(matches) < 1:
                msg = "'{}' isn't matched by any pattern".format(url)
                self.fail(msg)

            else:
                self.assertIs(extr1, matches[0][1], url)

    def test_init(self):
        """Test for exceptions in Extractor.initialize() and .finalize()"""
        def fail_request(*args, **kwargs):
            self.fail("called 'request() during initialization")

        for cls in extractor.extractors():
            if cls.category == "ytdl":
                continue
            extr = cls.from_url(cls.example)
            if not extr and cls.basecategory and not cls.instances:
                continue

            extr.request = fail_request
            extr.initialize()
            extr.finalize()

    @unittest.skipIf(sys.hexversion < 0x3060000, "test fails in CI")
    def test_init_ytdl(self):
        try:
            extr = extractor.find("ytdl:")
            extr.initialize()
            extr.finalize()
        except ImportError as exc:
            if exc.name in ("youtube_dl", "yt_dlp"):
                raise unittest.SkipTest("cannot import module '{}'".format(
                    exc.name))
            raise

    def test_docstrings(self):
        """Ensure docstring uniqueness"""
        for extr1 in extractor.extractors():
            for extr2 in extractor.extractors():
                if extr1 != extr2 and extr1.__doc__ and extr2.__doc__:
                    self.assertNotEqual(
                        extr1.__doc__,
                        extr2.__doc__,
                        "{} <-> {}".format(extr1, extr2),
                    )

    def test_names(self):
        """Ensure extractor classes are named CategorySubcategoryExtractor"""
        def capitalize(c):
            if "-" in c:
                return string.capwords(c.replace("-", " ")).replace(" ", "")
            return c.capitalize()

        for extr in extractor.extractors():
            if extr.category not in ("", "oauth", "ytdl"):
                expected = "{}{}Extractor".format(
                    capitalize(extr.category),
                    capitalize(extr.subcategory),
                )
                if expected[0].isdigit():
                    expected = "_" + expected
                self.assertEqual(expected, extr.__name__)


class TestExtractorWait(unittest.TestCase):

    def test_wait_seconds(self):
        extr = extractor.find("generic:https://example.org/")
        seconds = 5
        until = time.time() + seconds

        with patch("time.sleep") as sleep, patch.object(extr, "log") as log:
            extr.wait(seconds=seconds)

            sleep.assert_called_once_with(6.0)

            calls = log.info.mock_calls
            self.assertEqual(len(calls), 1)
            self._assert_isotime(calls[0][1][1], until)

    def test_wait_until(self):
        extr = extractor.find("generic:https://example.org/")
        until = time.time() + 5

        with patch("time.sleep") as sleep, patch.object(extr, "log") as log:
            extr.wait(until=until)

            calls = sleep.mock_calls
            self.assertEqual(len(calls), 1)
            self.assertAlmostEqual(calls[0][1][0], 6.0, places=1)

            calls = log.info.mock_calls
            self.assertEqual(len(calls), 1)
            self._assert_isotime(calls[0][1][1], until)

    def test_wait_until_datetime(self):
        extr = extractor.find("generic:https://example.org/")
        until = util.datetime_utcnow() + timedelta(seconds=5)
        until_local = datetime.now() + timedelta(seconds=5)

        if not until.microsecond:
            until = until.replace(microsecond=until_local.microsecond)

        with patch("time.sleep") as sleep, patch.object(extr, "log") as log:
            extr.wait(until=until)

            calls = sleep.mock_calls
            self.assertEqual(len(calls), 1)
            self.assertAlmostEqual(calls[0][1][0], 6.0, places=1)

            calls = log.info.mock_calls
            self.assertEqual(len(calls), 1)
            self._assert_isotime(calls[0][1][1], until_local)

    def _assert_isotime(self, output, until):
        if not isinstance(until, datetime):
            until = datetime.fromtimestamp(until)
        o = self._isotime_to_seconds(output)
        u = self._isotime_to_seconds(until.time().isoformat()[:8])
        self.assertLessEqual(o-u, 1.0)

    @staticmethod
    def _isotime_to_seconds(isotime):
        parts = isotime.split(":")
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


class TextExtractorOAuth(unittest.TestCase):

    def test_oauth1(self):
        for category in ("flickr", "smugmug", "tumblr"):
            extr = extractor.find("oauth:" + category)

            with patch.object(extr, "_oauth1_authorization_flow") as m:
                for msg in extr:
                    pass
                self.assertEqual(len(m.mock_calls), 1)

    def test_oauth2(self):
        for category in ("deviantart", "reddit"):
            extr = extractor.find("oauth:" + category)

            with patch.object(extr, "_oauth2_authorization_code_grant") as m:
                for msg in extr:
                    pass
                self.assertEqual(len(m.mock_calls), 1)

    def test_oauth2_mastodon(self):
        extr = extractor.find("oauth:mastodon:pawoo.net")

        with patch.object(extr, "_oauth2_authorization_code_grant") as m, \
                patch.object(extr, "_register") as r:
            for msg in extr:
                pass
            self.assertEqual(len(r.mock_calls), 0)
            self.assertEqual(len(m.mock_calls), 1)

    def test_oauth2_mastodon_unknown(self):
        extr = extractor.find("oauth:mastodon:example.com")

        with patch.object(extr, "_oauth2_authorization_code_grant") as m, \
                patch.object(extr, "_register") as r:
            r.return_value = {
                "client-id"    : "foo",
                "client-secret": "bar",
            }

            for msg in extr:
                pass

            self.assertEqual(len(r.mock_calls), 1)
            self.assertEqual(len(m.mock_calls), 1)


if __name__ == "__main__":
    unittest.main()
