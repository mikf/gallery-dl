# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e621.net/ and https://e926.net/"""

from ..version import __version__
from .. import text
from . import danbooru


class E621Extractor(danbooru.DanbooruExtractor):
    """Base class for e621 extractors"""

    def __init__(self, match):
        self._init_category(match)
        self.instance = INSTANCES.get(self.category) or {}
        super().__init__(match)


HEADER = {"User-Agent": "gallery-dl/{} (by mikf)".format(__version__)}
INSTANCES = {
    "e621": {
        "root": "https://e621.net",
        "pattern": r"e621\.net",
        "headers": HEADER,
        # TODO: extract notes using the /notes.json API endpoint
        # ref: https://e621.net/help/api#notes
        "extended-metadata": False,
        "pools": "sort",
        "page-limit": 750,
        "per-page": 320,
        "request-interval-min": 1.0,
    },
    "e926": {
        "root": "https://e926.net",
        "pattern": r"e926\.net",
        "headers": HEADER,
        "extended-metadata": False,
        "pools": "sort",
        "page-limit": 750,
        "per-page": 320,
        "request-interval-min": 1.0,
    },
}

BASE_PATTERN = E621Extractor.update(INSTANCES)


class E621TagExtractor(E621Extractor, danbooru.DanbooruTagExtractor):
    """Extractor for e621 posts from tag searches"""
    pattern = BASE_PATTERN + r"/posts?(?:\?.*?tags=|/index/\d+/)([^&#]+)"
    test = (
        ("https://e621.net/posts?tags=anry", {
            "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
            "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
        }),
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
    pattern = BASE_PATTERN + r"/(?:explore/posts/)?popular(?:\?([^#]*))?"
    test = (
        ("https://e621.net/popular"),
        (("https://e621.net/explore/posts/popular"
          "?date=2019-06-01&scale=month"), {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": ">= 70",
        }),
    )

    def posts(self):
        if self.page_start is None:
            self.page_start = 1
        return self._pagination("/popular.json", self.params, True)


class E621FavoriteExtractor(E621Extractor):
    """Extractor for e621 favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "Favorites", "{user_id}")
    archive_fmt = "f_{user_id}_{id}"
    pattern = BASE_PATTERN + r"/favorites(?:\?([^#]*))?"
    test = (
        ("https://e621.net/favorites"),
        ("https://e621.net/favorites?page=2&user_id=53275", {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": "> 260",
        }),
    )

    def __init__(self, match):
        E621Extractor.__init__(self, match)
        self.query = text.parse_query(match.group(match.lastindex))

    def metadata(self):
        return {"user_id": self.query.get("user_id", "")}

    def posts(self):
        if self.page_start is None:
            self.page_start = 1
        return self._pagination("/favorites.json", self.query, True)
