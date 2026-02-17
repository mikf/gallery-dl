#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl import exception  # noqa E402
from gallery_dl.extractor.deviantart import (  # noqa E402
    DeviantartDeviationExtractor,
    DeviantartOAuthAPI,
)


class TestDeviantartMediaSourceHandling(unittest.TestCase):

    def _extractor(self):
        return DeviantartDeviationExtractor.from_url(
            "https://www.deviantart.com/user/art/title-12345")

    def test_commit_skips_target_without_media_source(self):
        extr = self._extractor()

        deviation = {"filename": "sample", "deviationid": "uuid-1"}
        self.assertIsNone(extr.commit(deviation, {"error": "forbidden"}))

    def test_update_content_default_keeps_preview_on_auth_errors(self):
        extr = self._extractor()

        def _raise_auth(*_args, **_kwargs):
            raise exception.AuthorizationError(
                "Only subscribers may have access to this download.")

        extr.api = types.SimpleNamespace(deviation_download=_raise_auth)

        deviation = {"deviationid": "uuid-2"}
        content = {"src": "https://example.invalid/preview.jpg"}

        extr._update_content_default(deviation, content)

        self.assertEqual(content["src"], "https://example.invalid/preview.jpg")
        self.assertNotIn("is_original", deviation)

    def test_api_download_raises_authorization_when_payload_has_no_source(self):
        extr = self._extractor()
        extr.extra = False
        api = DeviantartOAuthAPI(extr)
        api._call = lambda *_args, **_kwargs: {
            "error": "forbidden",
            "error_description":
            "Only subscribers may have access to this download.",
        }

        with self.assertRaises(exception.AuthorizationError):
            api.deviation_download("uuid-3")


if __name__ == "__main__":
    unittest.main()
