# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Gelbooru v0.2 sites"""

from . import booru
from .. import text, util, exception

from xml.etree import ElementTree
import collections
import re


class GelbooruV02Extractor(booru.BooruExtractor):
    basecategory = "gelbooru_v02"

    def _api_request(self, params):
        url = self.root + "/index.php?page=dapi&s=post&q=index"
        return ElementTree.fromstring(self.request(url, params=params).text)

    def _pagination(self, params):
        params["pid"] = self.page_start
        params["limit"] = self.per_page

        while True:
            root = self._api_request(params)
            for post in root:
                yield post.attrib

            if len(root) < self.per_page:
                return
            params["pid"] += 1

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(
            post["created_at"], "%a %b %d %H:%M:%S %z %Y")

    def _extended_tags(self, post, page=None):
        if not page:
            url = "{}/index.php?page=post&s=view&id={}".format(
                self.root, post["id"])
            page = self.request(url).text
        html = text.extract(page, '<ul id="tag-', '</ul>')[0]
        if html:
            tags = collections.defaultdict(list)
            pattern = re.compile(
                r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'&]+)", re.S)
            for tag_type, tag_name in pattern.findall(html):
                tags[tag_type].append(text.unquote(tag_name))
            for key, value in tags.items():
                post["tags_" + key] = " ".join(value)


BASE_PATTERN = GelbooruV02Extractor.update({
    "realbooru": {"root": "https://realbooru.com"},
    "rule34"   : {"root": "https://rule34.xxx"},
    "safebooru": {"root": "https://safebooru.org"},
    "tbib"     : {"root": "https://tbib.org"},
})


class GelbooruV02TagExtractor(GelbooruV02Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]+)"
    test = (
        ("https://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
            "content": "97e4bbf86c3860be18de384d02d544251afe1d45",
            "pattern": r"https?://.*rule34\.xxx/images/\d+/[0-9a-f]+\.jpg",
            "count": 1,
        }),
        ("https://safebooru.org/index.php?page=post&s=list&tags=bonocho", {
            "url": "17c61b386530cf4c30842c9f580d15ef1cd09586",
            "content": "e5ad4c5bf241b1def154958535bef6c2f6b733eb",
        }),
        ("https://realbooru.com/index.php?page=post&s=list&tags=wine", {
            "count": ">= 64",
        }),
        ("https://tbib.org/index.php?page=post&s=list&tags=yuyaiyaui", {
            "count": ">= 120",
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination({"tags" : self.tags})


class GelbooruV02PoolExtractor(GelbooruV02Extractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=pool&s=show&id=(\d+)"
    test = (
        ("https://rule34.xxx/index.php?page=pool&s=show&id=179", {
            "count": 3,
        }),
        ("https://safebooru.org/index.php?page=pool&s=show&id=11", {
            "count": 5,
        }),
        ("https://realbooru.com/index.php?page=pool&s=show&id=1", {
            "count": 3,
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)
        self.post_ids = ()

    def skip(self, num):
        self.page_start += num
        return num

    def metadata(self):
        url = "{}/index.php?page=pool&s=show&id={}".format(
            self.root, self.pool_id)
        page = self.request(url).text

        name, pos = text.extract(page, "<h4>Pool: ", "</h4>")
        if not name:
            raise exception.NotFoundError("pool")
        self.post_ids = text.extract_iter(
            page, 'class="thumb" id="p', '"', pos)

        return {
            "pool": text.parse_int(self.pool_id),
            "pool_name": text.unescape(name),
        }

    def posts(self):
        params = {}
        for params["id"] in util.advance(self.post_ids, self.page_start):
            for post in self._api_request(params):
                yield post.attrib


class GelbooruV02PostExtractor(GelbooruV02Extractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=view&id=(\d+)"
    test = (
        ("https://rule34.xxx/index.php?page=post&s=view&id=1995545", {
            "content": "97e4bbf86c3860be18de384d02d544251afe1d45",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": "danraku",
                "tags_character": "kashima_(kantai_collection)",
                "tags_copyright": "kantai_collection",
                "tags_general": str,
                "tags_metadata": str,
            },
        }),
        ("https://safebooru.org/index.php?page=post&s=view&id=1169132", {
            "url": "cf05e37a3c62b2d55788e2080b8eabedb00f999b",
            "content": "93b293b27dabd198afafabbaf87c49863ac82f27",
            "options": (("tags", True),),
            "keyword": {
                "tags_artist": "kawanakajima",
                "tags_character": "heath_ledger ronald_mcdonald the_joker",
                "tags_copyright": "dc_comics mcdonald's the_dark_knight",
                "tags_general": str,
            },
        }),
        ("https://realbooru.com/index.php?page=post&s=view&id=668483", {
            "url": "2421b5b0e15d5e20f9067090a8b0fd4114d3e7d9",
            "content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",
        }),
        ("https://tbib.org/index.php?page=post&s=view&id=9233957", {
            "url": "5a6ebe07bfff8e6d27f7c30b5480f27abcb577d2",
            "content": "1c3831b6fbaa4686e3c79035b5d98460b1c85c43",
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return self._pagination({"id": self.post_id})
