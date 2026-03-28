#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import unittest
from unittest.mock import Mock, patch

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import config, exception, util  # noqa E402
from gallery_dl.extractor.common import Extractor  # noqa E402


class ByparrExtractor(Extractor):
    category = "byparr"
    subcategory = "test"
    cookies_domain = ".example.org"
    pattern = r"byparr:"
    example = "byparr:"


def challenge_response(url):
    response = requests.Response()
    response.status_code = 403
    response.reason = "Forbidden"
    response.url = url
    response.headers = {"server": "cloudflare"}
    response._content = b"_cf_chl_opt"
    response.encoding = "utf-8"
    return response


def byparr_response(url):
    response = requests.Response()
    response.status_code = 200
    response.reason = "OK"
    response.url = "http://127.0.0.1:8191/v1"
    response.headers = {"Content-Type": "application/json"}
    response._content = util.json_dumps({
        "status": "ok",
        "message": "Success",
        "solution": {
            "url": url,
            "status": 200,
            "cookies": [{
                "name": "cf_clearance",
                "value": "token",
                "domain": ".example.org",
                "path": "/",
                "expires": -1,
                "secure": True,
            }],
            "userAgent": (
                "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) "
                "Gecko/20100101 Firefox/140.0"
            ),
            "headers": {
                "Content-Type": "text/html; charset=utf-8",
            },
            "response": "<html><title>ok</title></html>",
        },
    }).encode()
    response.encoding = "utf-8"
    return response


class TestByparr(unittest.TestCase):

    def tearDown(self):
        config.clear()

    def _extractor(self, byparr=True):
        config.set(("extractor", "byparr", "test"), "byparr", byparr)
        extr = ByparrExtractor.from_url("byparr:")
        extr.initialize()
        return extr

    def test_request_solves_challenge_via_byparr(self):
        url = "https://example.org/gallery"
        extr = self._extractor()
        extr.session.request = Mock(return_value=challenge_response(url))

        with patch(
            "gallery_dl.extractor.common.requests.post",
            return_value=byparr_response(url),
        ) as post:
            response = extr.request(url, retries=0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "<html><title>ok</title></html>")
        self.assertEqual(
            extr.session.headers["User-Agent"],
            ("Mozilla/5.0 (X11; Linux x86_64; rv:140.0) "
             "Gecko/20100101 Firefox/140.0"),
        )
        self.assertEqual(
            extr.cookies.get("cf_clearance", domain=".example.org"),
            "token",
        )
        post.assert_called_once_with(
            "http://127.0.0.1:8191/v1",
            json={
                "cmd": "request.get",
                "url": url,
                "max_timeout": 60,
            },
            timeout=65,
        )

    def test_request_uses_custom_byparr_url_and_timeout(self):
        url = "https://example.org/gallery"
        extr = self._extractor({
            "url": "http://solver.local:8191",
            "timeout": 75,
        })
        extr.session.request = Mock(return_value=challenge_response(url))

        with patch(
            "gallery_dl.extractor.common.requests.post",
            return_value=byparr_response(url + "?page=2"),
        ) as post:
            extr.request(url, params={"page": 2}, retries=0)

        post.assert_called_once_with(
            "http://solver.local:8191/v1",
            json={
                "cmd": "request.get",
                "url": url + "?page=2",
                "max_timeout": 75,
            },
            timeout=80,
        )

    def test_request_does_not_use_byparr_for_post_requests(self):
        url = "https://example.org/api"
        extr = self._extractor()
        extr.session.request = Mock(return_value=challenge_response(url))

        with patch("gallery_dl.extractor.common.requests.post") as post:
            with self.assertRaises(exception.ChallengeError):
                extr.request(url, method="POST", data=b"{}", retries=0)

        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
