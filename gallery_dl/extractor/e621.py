# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e621.net/"""

from .common import Extractor, Message
from . import danbooru

BASE_PATTERN = r"(?:https?://)?e(621|926)\.net"


class E621Extractor(danbooru.DanbooruExtractor):
    """Base class for e621 extractors"""
    category = "e621"
    filename_fmt = "{category}_{id}_{file[md5]}.{extension}"
    page_limit = 750
    page_start = None
    per_page = 320
    request_interval_min = 1.0

    def __init__(self, match):
        super().__init__(match)
        self.root = "https://e{}.net".format(match.group(1))
        self.headers = {"User-Agent": "gallery-dl/1.14.0 (by mikf)"}

    def request(self, url, **kwargs):
        kwargs["headers"] = self.headers
        return Extractor.request(self, url, **kwargs)

    def items(self):
        data = self.metadata()
        for post in self.posts():
            file = post["file"]

            if not file["url"]:
                md5 = file["md5"]
                file["url"] = "https://static1.{}/data/{}/{}/{}.{}".format(
                    self.root[8:], md5[0:2], md5[2:4], md5, file["ext"])

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
            "url": "1bd09a72715286a79eea3b7f09f51b3493eb579a",
            "content": "91abe5d5334425d9787811d7f06d34c77974cd22",
        }),
        ("https://e621.net/pool/show/73"),
    )

    def posts(self):
        self.log.info("Fetching posts of pool %s", self.pool_id)

        id_to_post = {
            post["id"]: post
            for post in self._pagination(
                "/posts.json", {"tags": "pool:" + self.pool_id})
        }

        posts = []
        append = posts.append
        for num, pid in enumerate(self.post_ids, 1):
            if pid in id_to_post:
                post = id_to_post[pid]
                post["num"] = num
                append(post)
            else:
                self.log.warning("Post %s is unavailable", pid)

        return posts


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
