# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e621.net/"""

from .common import Extractor, Message
from . import danbooru
import time


BASE_PATTERN = r"(?:https?://)?e(621|926)\.net"


class E621Extractor(danbooru.DanbooruExtractor):
    """Base class for e621 extractors"""
    category = "e621"
    filename_fmt = "{category}_{id}_{file[md5]}.{extension}"
    page_limit = 750
    page_start = None
    per_page = 320
    _last_request = 0

    def __init__(self, match):
        super().__init__(match)
        self.root = "https://e{}.net".format(match.group(1))

    def request(self, url, **kwargs):
        diff = time.time() - E621Extractor._last_request
        if diff < 1.0:
            delay = 1.0 - diff
            self.log.debug("Sleeping for %s seconds", delay)
            time.sleep(delay)
        kwargs["headers"] = {"User-Agent": "gallery-dl/1.14.0 (by mikf)"}
        response = Extractor.request(self, url, **kwargs)
        E621Extractor._last_request = time.time()
        return response

    def items(self):
        data = self.metadata()
        for post in self.posts():
            file = post["file"]

            if not file["url"]:
                ihash = file["md5"]
                file["url"] = "https://static1.{}/data/{}/{}/{}.{}".format(
                    self.root[8:], ihash[0:2], ihash[2:4], ihash, file["ext"])

            post["filename"] = file["md5"]
            post["extension"] = file["ext"]
            post.update(data)
            yield Message.Directory, post
            yield Message.Url, file["url"], post


class E621TagExtractor(E621Extractor, danbooru.DanbooruTagExtractor):
    """Extractor for e621 posts from tag searches"""
    pattern = BASE_PATTERN + r"/posts?(?:\?.*?tags=|/index/\d+/)([^&#]+)"
    test = (
        ("https://e621.net/posts?tags=anry", {
            "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
            "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
        }),
        ("https://e926.net/posts?tags=anry"),
        ("https://e621.net/post/index/1/anry"),
        ("https://e621.net/post?tags=anry"),
    )


class E621PoolExtractor(E621Extractor, danbooru.DanbooruPoolExtractor):
    """Extractor for e621 pools"""
    pattern = BASE_PATTERN + r"/pool(?:s|/show)/(\d+)"
    test = (
        ("https://e621.net/pools/73", {
            "url": "842f2fb065c7c339486a9b1d689020b8569888ed",
            "content": "c2c87b7a9150509496cddc75ccab08109922876a",
        }),
        ("https://e621.net/pool/show/73"),
    )


class E621PostExtractor(E621Extractor, danbooru.DanbooruPostExtractor):
    """Extractor for single e621 posts"""
    pattern = BASE_PATTERN + r"/post(?:s|/show)/(\d+)"
    test = (
        ("https://e621.net/posts/535", {
            "url": "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
            "content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
        }),
        ("https://e621.net/post/show/535"),
    )


class E621PopularExtractor(E621Extractor, danbooru.DanbooruPopularExtractor):
    """Extractor for popular images from e621"""
    pattern = BASE_PATTERN + r"/explore/posts/popular(?:\?([^#]*))?"
    test = (
        ("https://e621.net/explore/posts/popular"),
        (("https://e621.net/explore/posts/popular"
          "?date=2019-06-01&scale=month"), {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": ">= 70",
        })
    )
