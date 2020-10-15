#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest import mock

import logging
import tempfile
from os.path import join

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import config, extractor  # noqa E402


class TestCookiejar(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path = tempfile.TemporaryDirectory()

        cls.cookiefile = join(cls.path.name, "cookies.txt")
        with open(cls.cookiefile, "w") as file:
            file.write("""# HTTP Cookie File
.example.org\tTRUE\t/\tFALSE\t253402210800\tNAME\tVALUE
""")

        cls.invalid_cookiefile = join(cls.path.name, "invalid.txt")
        with open(cls.invalid_cookiefile, "w") as file:
            file.write("""# asd
.example.org\tTRUE/FALSE\t253402210800\tNAME\tVALUE
""")

    @classmethod
    def tearDownClass(cls):
        cls.path.cleanup()
        config.clear()

    def test_cookiefile(self):
        config.set((), "cookies", self.cookiefile)

        cookies = extractor.find("test:").session.cookies
        self.assertEqual(len(cookies), 1)

        cookie = next(iter(cookies))
        self.assertEqual(cookie.domain, ".example.org")
        self.assertEqual(cookie.path  , "/")
        self.assertEqual(cookie.name  , "NAME")
        self.assertEqual(cookie.value , "VALUE")

    def test_invalid_cookiefile(self):
        self._test_warning(self.invalid_cookiefile, ValueError)

    def test_invalid_filename(self):
        self._test_warning(join(self.path.name, "nothing"), FileNotFoundError)

    def _test_warning(self, filename, exc):
        config.set((), "cookies", filename)
        log = logging.getLogger("test")
        with mock.patch.object(log, "warning") as mock_warning:
            cookies = extractor.find("test:").session.cookies
            self.assertEqual(len(cookies), 0)
            self.assertEqual(mock_warning.call_count, 1)
            self.assertEqual(mock_warning.call_args[0][0], "cookies: %s")
            self.assertIsInstance(mock_warning.call_args[0][1], exc)


class TestCookiedict(unittest.TestCase):

    def setUp(self):
        self.cdict = {"NAME1": "VALUE1", "NAME2": "VALUE2"}
        config.set((), "cookies", self.cdict)

    def tearDown(self):
        config.clear()

    def test_dict(self):
        cookies = extractor.find("test:").session.cookies
        self.assertEqual(len(cookies), len(self.cdict))
        self.assertEqual(sorted(cookies.keys()), sorted(self.cdict.keys()))
        self.assertEqual(sorted(cookies.values()), sorted(self.cdict.values()))

    def test_domain(self):
        for category in ["exhentai", "nijie", "sankaku", "seiga"]:
            extr = _get_extractor(category)
            cookies = extr.session.cookies
            for key in self.cdict:
                self.assertTrue(key in cookies)
            for c in cookies:
                self.assertEqual(c.domain, extr.cookiedomain)


class TestCookieLogin(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def test_cookie_login(self):
        extr_cookies = {
            "exhentai": ("ipb_member_id", "ipb_pass_hash"),
            "nijie"   : ("nemail", "nlogin"),
            "sankaku" : ("login", "pass_hash"),
            "seiga"   : ("user_session",),
        }
        for category, cookienames in extr_cookies.items():
            cookies = {name: "value" for name in cookienames}
            config.set((), "cookies", cookies)
            extr = _get_extractor(category)
            with mock.patch.object(extr, "_login_impl") as mock_login:
                extr.login()
                mock_login.assert_not_called()


def _get_extractor(category):
    for extr in extractor.extractors():
        if extr.category == category and hasattr(extr, "_login_impl"):
            url = next(extr._get_tests())[0]
            return extr.from_url(url)


if __name__ == "__main__":
    unittest.main()
