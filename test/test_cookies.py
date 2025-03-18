#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest import mock

import time
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
        with open(cls.cookiefile, "w") as fp:
            fp.write("""# HTTP Cookie File
.example.org\tTRUE\t/\tFALSE\t253402210800\tNAME\tVALUE
""")

        cls.invalid_cookiefile = join(cls.path.name, "invalid.txt")
        with open(cls.invalid_cookiefile, "w") as fp:
            fp.write("""# asd
.example.org\tTRUE/FALSE\t253402210800\tNAME\tVALUE
""")

    @classmethod
    def tearDownClass(cls):
        cls.path.cleanup()
        config.clear()

    def test_cookiefile(self):
        config.set((), "cookies", self.cookiefile)
        cookies = _get_extractor("test").cookies
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
        log = logging.getLogger("generic")

        with mock.patch.object(log, "warning") as mock_warning:
            cookies = _get_extractor("test").cookies

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
        cookies = _get_extractor("test").cookies

        self.assertEqual(len(cookies), len(self.cdict))
        self.assertEqual(sorted(cookies.keys()), sorted(self.cdict.keys()))
        self.assertEqual(sorted(cookies.values()), sorted(self.cdict.values()))

    def test_domain(self):
        for category in ["exhentai", "idolcomplex", "nijie", "horne"]:
            extr = _get_extractor(category)
            cookies = extr.cookies
            for key in self.cdict:
                self.assertTrue(key in cookies)
            for c in cookies:
                self.assertEqual(c.domain, extr.cookies_domain)


class TestCookieLogin(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def test_cookie_login(self):
        extr_cookies = {
            "exhentai"   : ("ipb_member_id", "ipb_pass_hash"),
            "idolcomplex": ("login", "pass_hash"),
            "nijie"      : ("nijie_tok",),
            "horne"      : ("horne_tok",),
        }
        for category, cookienames in extr_cookies.items():
            cookies = {name: "value" for name in cookienames}
            config.set((), "cookies", cookies)
            extr = _get_extractor(category)
            with mock.patch.object(extr, "_login_impl") as mock_login:
                extr.login()
                mock_login.assert_not_called()


class TestCookieUtils(unittest.TestCase):

    def test_check_cookies(self):
        extr = _get_extractor("test")
        self.assertFalse(extr.cookies, "empty")
        self.assertFalse(extr.cookies_domain, "empty")

        # always returns False when checking for empty cookie list
        self.assertFalse(extr.cookies_check(()))

        self.assertFalse(extr.cookies_check(("a",)))
        self.assertFalse(extr.cookies_check(("a", "b")))
        self.assertFalse(extr.cookies_check(("a", "b", "c")))

        extr.cookies.set("a", "1")
        self.assertTrue(extr.cookies_check(("a",)))
        self.assertFalse(extr.cookies_check(("a", "b")))
        self.assertFalse(extr.cookies_check(("a", "b", "c")))

        extr.cookies.set("b", "2")
        self.assertTrue(extr.cookies_check(("a",)))
        self.assertTrue(extr.cookies_check(("a", "b")))
        self.assertFalse(extr.cookies_check(("a", "b", "c")))

    def test_check_cookies_domain(self):
        extr = _get_extractor("test")
        self.assertFalse(extr.cookies, "empty")
        extr.cookies_domain = ".example.org"

        self.assertFalse(extr.cookies_check(("a",)))
        self.assertFalse(extr.cookies_check(("a", "b")))

        extr.cookies.set("nd_a", "1")
        self.assertFalse(extr.cookies_check(("nd_a",)))

        extr.cookies.set("cd_a", "1", domain=extr.cookies_domain)
        self.assertTrue(extr.cookies_check(("cd_a",)))

        extr.cookies.set("wd_a", "1", domain="www" + extr.cookies_domain)
        self.assertFalse(extr.cookies_check(("wd_a",)))
        self.assertEqual(len(extr.cookies), 3)

        extr.cookies.set("cd_b", "2", domain=extr.cookies_domain)
        extr.cookies.set("cd_c", "3", domain=extr.cookies_domain)
        self.assertFalse(extr.cookies_check(("nd_a", "cd_b", "cd_c")))
        self.assertTrue(extr.cookies_check(("cd_a", "cd_b", "cd_c")))
        self.assertFalse(extr.cookies_check(("wd_a", "cd_b", "cd_c")))
        self.assertEqual(len(extr.cookies), 5)

    def test_check_cookies_domain_sub(self):
        extr = _get_extractor("test")
        self.assertFalse(extr.cookies, "empty")
        extr.cookies_domain = ".example.org"

        self.assertFalse(extr.cookies_check(("a",), subdomains=True))
        self.assertFalse(extr.cookies_check(("a", "b"), subdomains=True))

        extr.cookies.set("nd_a", "1")
        self.assertFalse(extr.cookies_check(("nd_a",), subdomains=True))

        extr.cookies.set("cd_a", "1", domain=extr.cookies_domain)
        self.assertTrue(extr.cookies_check(("cd_a",), subdomains=True))

        extr.cookies.set("wd_a", "1", domain="www" + extr.cookies_domain)
        self.assertTrue(extr.cookies_check(("wd_a",), subdomains=True))

        extr.cookies.set("cd_b", "2", domain=extr.cookies_domain)
        extr.cookies.set("cd_c", "3", domain=extr.cookies_domain)
        self.assertEqual(len(extr.cookies), 5)
        self.assertFalse(extr.cookies_check(
            ("nd_a", "cd_b", "cd_c"), subdomains=True))
        self.assertTrue(extr.cookies_check(
            ("cd_a", "cd_b", "cd_c"), subdomains=True))
        self.assertTrue(extr.cookies_check(
            ("wd_a", "cd_b", "cd_c"), subdomains=True))

    def test_check_cookies_expires(self):
        extr = _get_extractor("test")
        self.assertFalse(extr.cookies, "empty")
        self.assertFalse(extr.cookies_domain, "empty")

        now = int(time.time())
        log = logging.getLogger("generic")

        extr.cookies.set("a", "1", expires=now-100)
        with mock.patch.object(log, "warning") as mw:
            self.assertFalse(extr.cookies_check(("a",)))
            self.assertEqual(mw.call_count, 1)
            self.assertEqual(mw.call_args[0], ("Cookie '%s' has expired", "a"))

        extr.cookies.set("a", "1", expires=now+100)
        with mock.patch.object(log, "warning") as mw:
            self.assertTrue(extr.cookies_check(("a",)))
            self.assertEqual(mw.call_count, 1)
            self.assertEqual(mw.call_args[0], (
                "Cookie '%s' will expire in less than %s hour%s", "a", 1, ""))

        extr.cookies.set("a", "1", expires=now+100+7200)
        with mock.patch.object(log, "warning") as mw:
            self.assertTrue(extr.cookies_check(("a",)))
            self.assertEqual(mw.call_count, 1)
            self.assertEqual(mw.call_args[0], (
                "Cookie '%s' will expire in less than %s hour%s", "a", 3, "s"))

        extr.cookies.set("a", "1", expires=now+100+24*3600)
        with mock.patch.object(log, "warning") as mw:
            self.assertTrue(extr.cookies_check(("a",)))
            self.assertEqual(mw.call_count, 0)


def _get_extractor(category):
    extr = extractor.find(URLS[category])
    extr.initialize()
    return extr


URLS = {
    "exhentai"   : "https://exhentai.org/g/1200119/d55c44d3d0/",
    "idolcomplex": "https://idol.sankakucomplex.com/post/show/1",
    "nijie"      : "https://nijie.info/view.php?id=1",
    "horne"      : "https://horne.red/view.php?id=1",
    "test"       : "generic:https://example.org/",
}


if __name__ == "__main__":
    unittest.main()
