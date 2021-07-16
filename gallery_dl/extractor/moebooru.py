# -*- coding: utf-8 -*-

# Copyright 2020-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Moebooru based sites"""

from .booru import BooruExtractor
from .. import text

import collections
import datetime
import re


class MoebooruExtractor(BooruExtractor):
    """Base class for Moebooru extractors"""
    basecategory = "moebooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_start = 1

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_timestamp(post["created_at"])

    def _extended_tags(self, post):
        url = "{}/post/show/{}".format(self.root, post["id"])
        page = self.request(url).text
        html = text.extract(page, '<ul id="tag-', '</ul>')[0]
        if html:
            tags = collections.defaultdict(list)
            pattern = re.compile(r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'+]+)")
            for tag_type, tag_name in pattern.findall(html):
                tags[tag_type].append(text.unquote(tag_name))
            for key, value in tags.items():
                post["tags_" + key] = " ".join(value)

    def _pagination(self, url, params):
        params["page"] = self.page_start
        params["limit"] = self.per_page

        while True:
            posts = self.request(url, params=params).json()
            yield from posts

            if len(posts) < self.per_page:
                return
            params["page"] += 1


BASE_PATTERN = MoebooruExtractor.update({
    "yandere": {
        "root": "https://yande.re",
    },
    "konachan": {
        "root": "https://konachan.com",
        "pattern": r"konachan\.(?:com|net)",
    },
    "hypnohub": {
        "root": "https://hypnohub.net",
    },
    "sakugabooru": {
        "root": "https://www.sakugabooru.com",
        "pattern": r"(?:www\.)?sakugabooru\.com",
    },
    "lolibooru": {
        "root": "https://lolibooru.moe",
    },
})


class MoebooruPostExtractor(MoebooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post/show/(\d+)"
    test = (
        ("https://yande.re/post/show/51824", {
            "content": "59201811c728096b2d95ce6896fd0009235fe683",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": "sasaki_tamaru",
                "tags_circle": "softhouse_chara",
                "tags_copyright": "ouzoku",
                "tags_general": str,
            },
        }),
        ("https://konachan.com/post/show/205189", {
            "content": "674e75a753df82f5ad80803f575818b8e46e4b65",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": "patata",
                "tags_character": "clownpiece",
                "tags_copyright": "touhou",
                "tags_general": str,
            },
        }),
        ("https://konachan.net/post/show/205189"),
        ("https://hypnohub.net/post/show/73964", {
            "content": "02d5f5a8396b621a6efc04c5f8ef1b7225dfc6ee",
        }),
        ("https://www.sakugabooru.com/post/show/125570"),
        ("https://lolibooru.moe/post/show/287835"),
    )

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        params = {"tags": "id:" + self.post_id}
        return self.request(self.root + "/post.json", params=params).json()


class MoebooruTagExtractor(MoebooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/post\?(?:[^&#]*&)*tags=([^&#]+)"
    test = (
        ("https://yande.re/post?tags=ouzoku+armor", {
            "content": "59201811c728096b2d95ce6896fd0009235fe683",
        }),
        ("https://konachan.com/post?tags=patata", {
            "content": "838cfb815e31f48160855435655ddf7bfc4ecb8d",
        }),
        ("https://konachan.net/post?tags=patata"),
        ("https://hypnohub.net/post?tags=gonoike_biwa", {
            "url": "072330c34a1e773d0cafd00e64b8060d34b078b6",
        }),
        ("https://www.sakugabooru.com/post?tags=nichijou"),
        ("https://lolibooru.moe/post?tags=ruu_%28tksymkw%29"),
    )

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination(self.root + "/post.json", params)


class MoebooruPoolExtractor(MoebooruExtractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/pool/show/(\d+)"
    test = (
        ("https://yande.re/pool/show/318", {
            "content": "2a35b9d6edecce11cc2918c6dce4de2198342b68",
        }),
        ("https://konachan.com/pool/show/95", {
            "content": "cf0546e38a93c2c510a478f8744e60687b7a8426",
        }),
        ("https://konachan.net/pool/show/95"),
        ("https://hypnohub.net/pool/show/61", {
            "url": "fd74991c8729e77acd3c35eb6ddc4128ff445adf",
        }),
        ("https://www.sakugabooru.com/pool/show/54"),
        ("https://lolibooru.moe/pool/show/239"),
    )

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)

    def metadata(self):
        return {"pool": text.parse_int(self.pool_id)}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination(self.root + "/post.json", params)


class MoebooruPopularExtractor(MoebooruExtractor):
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + \
        r"/post/popular_(by_(?:day|week|month)|recent)(?:\?([^#]*))?"
    test = (
        ("https://yande.re/post/popular_by_month?month=6&year=2014", {
            "count": 40,
        }),
        ("https://yande.re/post/popular_recent"),
        ("https://konachan.com/post/popular_by_month?month=11&year=2010", {
            "count": 20,
        }),
        ("https://konachan.com/post/popular_recent"),
        ("https://konachan.net/post/popular_recent"),
        ("https://hypnohub.net/post/popular_by_month?month=6&year=2014", {
            "count": 20,
        }),
        ("https://hypnohub.net/post/popular_recent"),
        ("https://www.sakugabooru.com/post/popular_recent"),
        ("https://lolibooru.moe/post/popular_recent"),
    )

    def __init__(self, match):
        MoebooruExtractor.__init__(self, match)
        self.scale = match.group(match.lastindex-1)
        self.query = match.group(match.lastindex)

    def metadata(self):
        self.params = params = text.parse_query(self.query)

        if "year" in params:
            date = "{:>04}-{:>02}-{:>02}".format(
                params["year"],
                params.get("month", "01"),
                params.get("day", "01"),
            )
        else:
            date = datetime.date.today().isoformat()

        scale = self.scale
        if scale.startswith("by_"):
            scale = scale[3:]
        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        url = "{}/post/popular_{}.json".format(self.root, self.scale)
        return self.request(url, params=self.params).json()
