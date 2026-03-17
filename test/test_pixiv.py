#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gallery_dl.extractor.pixiv import PixivBookmarkExtractorMixin  # noqa E402


class _DummyLog():
    def __init__(self):
        self.messages = []

    def debug(self, msg, *args):
        self.messages.append(msg % args if args else msg)


class _DummyBookmarkBase():
    def __init__(self, config):
        self._config = config
        self.log = _DummyLog()
        self.max_posts = 0

    def _init(self):
        self.max_posts = self.config("max-posts", 0)

    def config(self, key, default=None):
        return self._config.get(key, default)

    def config2(self, key, key2, default=None):
        if key in self._config:
            return self._config[key]
        return self._config.get(key2, default)


class DummyBookmarkExtractor(PixivBookmarkExtractorMixin, _DummyBookmarkBase):
    bookmark_items_key = "novels"

    def __init__(self, pages, config=None, query=None):
        _DummyBookmarkBase.__init__(self, config or {})
        self.query = query or {}
        self.pages = {
            ((self._params_key(params) if hasattr(params, "items")
              else params)): data
            for params, data in pages.items()
        }
        self.calls = []
        self._bookmark_state_init()

    @staticmethod
    def _params_key(params):
        return tuple(sorted(
            (key, str(value))
            for key, value in params.items()
            if value is not None
        ))

    def _bookmark_list_params(self):
        return {"user_id": "1", "tag": None, "restrict": "private"}

    def _bookmark_page(self, params):
        key = self._params_key(params)
        self.calls.append(key)
        return self.pages[key]

    def _bookmark_fast_skip_enabled(self):
        return not (self.config("covers") or self.config("embeds"))


class TestPixivBookmarkSkip(unittest.TestCase):
    def test_skip_files_uses_cursor_pages_and_buffers_remainder(self):
        first = {
            "user_id": "1",
            "restrict": "private",
        }
        second = {
            "user_id": "1",
            "restrict": "private",
            "max_bookmark_id": "99",
        }
        pages = {
            tuple(sorted(first.items())): {
                "novels": [{"id": num} for num in range(30)],
                "next_url": ("https://app-api.pixiv.net/v1/user/bookmarks/"
                             "novel?user_id=1&restrict=private"
                             "&max_bookmark_id=99"),
            },
            tuple(sorted(second.items())): {
                "novels": [{"id": num} for num in range(30, 60)],
                "next_url": ("https://app-api.pixiv.net/v1/user/bookmarks/"
                             "novel?user_id=1&restrict=private"
                             "&max_bookmark_id=49"),
            },
        }

        extr = DummyBookmarkExtractor(pages, config={"file-range": "51-55"})
        extr._init()

        self.assertEqual(extr.skip_files(51), 50)
        self.assertEqual(len(extr.calls), 2)
        self.assertIn("Fast-skipped 50 bookmark items in 2 page(s)",
                      extr.log.messages)

        items = list(itertools.islice(extr._bookmark_iter(), 5))
        self.assertEqual([item["id"] for item in items], [50, 51, 52, 53, 54])
        self.assertEqual(len(extr.calls), 2)

    def test_range_limit_caps_max_posts_for_contiguous_ranges(self):
        extr = DummyBookmarkExtractor({}, config={"file-range": "51-55"})
        extr._init()
        self.assertEqual(extr.max_posts, 5)

    def test_range_limit_accepts_legacy_image_range_alias(self):
        extr = DummyBookmarkExtractor({}, config={"image-range": "51-55"})
        extr._init()
        self.assertEqual(extr.max_posts, 5)

    def test_range_limit_ignores_sparse_ranges(self):
        extr = DummyBookmarkExtractor(
            {}, config={"file-range": "51,53,55", "max-posts": 9})
        extr._init()
        self.assertEqual(extr.max_posts, 9)

    def test_range_limit_disabled_when_covers_are_enabled(self):
        extr = DummyBookmarkExtractor(
            {}, config={"file-range": "51-55", "max-posts": 9, "covers": True})
        extr._init()
        self.assertEqual(extr.max_posts, 9)

    def test_skip_files_disabled_when_embeds_are_enabled(self):
        first = {
            "user_id": "1",
            "restrict": "private",
        }
        pages = {
            tuple(sorted(first.items())): {
                "novels": [{"id": num} for num in range(30)],
                "next_url": None,
            },
        }

        extr = DummyBookmarkExtractor(
            pages, config={"file-range": "51-55", "embeds": True})
        extr._init()

        self.assertEqual(extr.skip_files(51), 0)
        self.assertEqual(extr.calls, [])


if __name__ == "__main__":
    unittest.main()
