#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import unittest
import requests

from gallery_dl import text
from gallery_dl.util import OAuthSession

TESTSERVER = "http://oauthbin.com"
CONSUMER_KEY = "key"
CONSUMER_SECRET = "secret"
REQUEST_TOKEN = "requestkey"
REQUEST_TOKEN_SECRET = "requestsecret"
ACCESS_TOKEN = "accesskey"
ACCESS_TOKEN_SECRET = "accesssecret"


class TestOAuthSession(unittest.TestCase):

    def test_concat(self):
        concat = OAuthSession.concat

        self.assertEqual(concat(), "")
        self.assertEqual(concat("str"), "str")
        self.assertEqual(concat("str1", "str2"), "str1&str2")

        self.assertEqual(concat("&", "?/"), "%26&%3F%2F")
        self.assertEqual(
            concat("GET", "http://example.org/", "foo=bar&baz=a"),
            "GET&http%3A%2F%2Fexample.org%2F&foo%3Dbar%26baz%3Da"
        )

    def test_nonce(self, N=16):
        nonce_values = set(OAuthSession.nonce(N) for _ in range(N))

        # uniqueness
        self.assertEqual(len(nonce_values), N)

        # length
        for nonce in nonce_values:
            self.assertEqual(len(nonce), N)

    def test_quote(self):
        quote = OAuthSession.quote

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

    def test_urlencode(self):
        urlencode = OAuthSession.urlencode

        self.assertEqual(urlencode({}), "")
        self.assertEqual(urlencode({"foo": "bar"}), "foo=bar")

        self.assertEqual(
            urlencode({"foo": "bar", "baz": "a", "a": "baz"}),
            "a=baz&baz=a&foo=bar"
        )
        self.assertEqual(
            urlencode({
                "oauth_consumer_key": "0685bd9184jfhq22",
                "oauth_token": "ad180jjd733klru7",
                "oauth_signature_method": "HMAC-SHA1",
                "oauth_timestamp": 137131200,
                "oauth_nonce": "4572616e48616d6d65724c61686176",
                "oauth_version": "1.0"
            }),
            "oauth_consumer_key=0685bd9184jfhq22&"
            "oauth_nonce=4572616e48616d6d65724c61686176&"
            "oauth_signature_method=HMAC-SHA1&"
            "oauth_timestamp=137131200&"
            "oauth_token=ad180jjd733klru7&"
            "oauth_version=1.0"
        )

    def test_request_token(self):
        response = self._oauth_request(
            "/v1/request-token", {})
        expected = "oauth_token=requestkey&oauth_token_secret=requestsecret"
        self.assertEqual(response, expected, msg=response)

        data = text.parse_query(response)
        self.assertTrue(data["oauth_token"], REQUEST_TOKEN)
        self.assertTrue(data["oauth_token_secret"], REQUEST_TOKEN_SECRET)

    def test_access_token(self):
        response = self._oauth_request(
            "/v1/access-token", {}, REQUEST_TOKEN, REQUEST_TOKEN_SECRET)
        expected = "oauth_token=accesskey&oauth_token_secret=accesssecret"
        self.assertEqual(response, expected, msg=response)

        data = text.parse_query(response)
        self.assertTrue(data["oauth_token"], ACCESS_TOKEN)
        self.assertTrue(data["oauth_token_secret"], ACCESS_TOKEN_SECRET)

    def test_authenticated_call(self):
        params = {"method": "foo", "bar": "baz", "a": "äöüß/?&#"}
        response = self._oauth_request(
            "/v1/echo", params, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        expected = OAuthSession.urlencode(params)

        self.assertEqual(response, expected, msg=response)
        self.assertEqual(text.parse_query(response), params)

    def _oauth_request(self, endpoint, params=None,
                       oauth_token=None, oauth_token_secret=None):
        session = OAuthSession(
            requests.session(),
            CONSUMER_KEY, CONSUMER_SECRET,
            oauth_token, oauth_token_secret,
        )
        url = TESTSERVER + endpoint
        return session.get(url, params.copy()).text


if __name__ == "__main__":
    unittest.main(warnings="ignore")
