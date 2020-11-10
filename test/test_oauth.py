#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import oauth, text  # noqa E402

TESTSERVER = "http://term.ie/oauth/example"
CONSUMER_KEY = "key"
CONSUMER_SECRET = "secret"
REQUEST_TOKEN = "requestkey"
REQUEST_TOKEN_SECRET = "requestsecret"
ACCESS_TOKEN = "accesskey"
ACCESS_TOKEN_SECRET = "accesssecret"


class TestOAuthSession(unittest.TestCase):

    def test_concat(self):
        concat = oauth.concat

        self.assertEqual(concat(), "")
        self.assertEqual(concat("str"), "str")
        self.assertEqual(concat("str1", "str2"), "str1&str2")

        self.assertEqual(concat("&", "?/"), "%26&%3F%2F")
        self.assertEqual(
            concat("GET", "http://example.org/", "foo=bar&baz=a"),
            "GET&http%3A%2F%2Fexample.org%2F&foo%3Dbar%26baz%3Da"
        )

    def test_nonce(self, size=16):
        nonce_values = set(oauth.nonce(size) for _ in range(size))

        # uniqueness
        self.assertEqual(len(nonce_values), size)

        # length
        for nonce in nonce_values:
            self.assertEqual(len(nonce), size)

    def test_quote(self):
        quote = oauth.quote

        reserved = ",;:!\"§$%&/(){}[]=?`´+*'äöü"
        unreserved = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "abcdefghijklmnopqrstuvwxyz"
                      "0123456789-._~")

        for char in unreserved:
            self.assertEqual(quote(char), char)

        for char in reserved:
            quoted = quote(char)
            quoted_hex = quoted.replace("%", "")
            self.assertTrue(quoted.startswith("%"))
            self.assertTrue(len(quoted) >= 3)
            self.assertEqual(quoted_hex.upper(), quoted_hex)

    def test_request_token(self):
        response = self._oauth_request(
            "/request_token.php", {})
        expected = "oauth_token=requestkey&oauth_token_secret=requestsecret"
        self.assertEqual(response, expected, msg=response)

        data = text.parse_query(response)
        self.assertTrue(data["oauth_token"], REQUEST_TOKEN)
        self.assertTrue(data["oauth_token_secret"], REQUEST_TOKEN_SECRET)

    def test_access_token(self):
        response = self._oauth_request(
            "/access_token.php", {}, REQUEST_TOKEN, REQUEST_TOKEN_SECRET)
        expected = "oauth_token=accesskey&oauth_token_secret=accesssecret"
        self.assertEqual(response, expected, msg=response)

        data = text.parse_query(response)
        self.assertTrue(data["oauth_token"], ACCESS_TOKEN)
        self.assertTrue(data["oauth_token_secret"], ACCESS_TOKEN_SECRET)

    def test_authenticated_call(self):
        params = {"method": "foo", "a": "äöüß/?&#", "äöüß/?&#": "a"}
        response = self._oauth_request(
            "/echo_api.php", params, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        self.assertEqual(text.parse_query(response), params)

    def _oauth_request(self, endpoint, params=None,
                       oauth_token=None, oauth_token_secret=None):
        # the test server at 'term.ie' is unreachable
        raise unittest.SkipTest()

        session = oauth.OAuth1Session(
            CONSUMER_KEY, CONSUMER_SECRET,
            oauth_token, oauth_token_secret,
        )
        try:
            response = session.get(TESTSERVER + endpoint, params=params)
            response.raise_for_status()
            return response.text
        except OSError:
            raise unittest.SkipTest()


if __name__ == "__main__":
    unittest.main(warnings="ignore")
