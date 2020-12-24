# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for *booru sites"""

from .common import Extractor, Message, generate_extractors
from .. import text, util, exception

from xml.etree import ElementTree
import collections
import operator
import re


class BooruExtractor(Extractor):
    """Base class for *booru extractors"""
    basecategory = "booru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_start = 0
    per_page = 100

    def items(self):
        self.login()
        data = self.metadata()
        tags = self.config("tags", False)

        for post in self.posts():
            try:
                url = self._file_url(post)
                if url[0] == "/":
                    url = self.root + url
            except (KeyError, TypeError):
                self.log.debug("Unable to fetch download URL for post %s "
                               "(md5: %s)", post.get("id"), post.get("md5"))
                continue

            if tags:
                self._extended_tags(post)
            self._prepare(post)
            post.update(data)
            text.nameext_from_url(url, post)

            yield Message.Directory, post
            yield Message.Url, url, post

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def login(self):
        """Login and set necessary cookies"""

    def metadata(self):
        """Return a dict with general metadata"""
        return ()

    def posts(self):
        """Return an iterable with post objects"""
        return ()

    _file_url = operator.itemgetter("file_url")

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


class BooruPostExtractor(BooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern_fmt = r"/index\.php\?page=post&s=view&id=(\d+)"

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return self._pagination({"id": self.post_id})


class BooruTagExtractor(BooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern_fmt = r"/index\.php\?page=post&s=list&tags=([^&#]+)"

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1).replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination({"tags" : self.tags})


class BooruPoolExtractor(BooruExtractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern_fmt = r"/index\.php\?page=pool&s=show&id=(\d+)"

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
        self.pool_id = match.group(1)
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


EXTRACTORS = {
    "rule34": {
        "root": "https://rule34.xxx",
        "test-tag": (
            ("https://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
                "content": "97e4bbf86c3860be18de384d02d544251afe1d45",
                "pattern": r"https?://.*rule34\.xxx/images/\d+/[0-9a-f]+\.jpg",
                "count": 1,
            }),
        ),
        "test-pool": (
            ("https://rule34.xxx/index.php?page=pool&s=show&id=179", {
                "count": 3,
            }),
        ),
        "test-post": (
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
        ),
    },
    "safebooru": {
        "root": "https://safebooru.org",
        "test-tag": (
            ("https://safebooru.org/index.php?page=post&s=list&tags=bonocho", {
                "url": "17c61b386530cf4c30842c9f580d15ef1cd09586",
                "content": "e5ad4c5bf241b1def154958535bef6c2f6b733eb",
            }),
        ),
        "test-pool": (
            ("https://safebooru.org/index.php?page=pool&s=show&id=11", {
                "count": 5,
            }),
        ),
        "test-post": (
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
        ),
    },
    "realbooru": {
        "root": "https://realbooru.com",
        "test-tag": (
            ("https://realbooru.com/index.php?page=post&s=list&tags=wine", {
                "count": ">= 64",
            }),
        ),
        "test-pool": (
            ("https://realbooru.com/index.php?page=pool&s=show&id=1", {
                "count": 3,
            }),
        ),
        "test-post": (
            ("https://realbooru.com/index.php?page=post&s=view&id=668483", {
                "url": "2421b5b0e15d5e20f9067090a8b0fd4114d3e7d9",
                "content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",
            }),
        ),
    },
}

generate_extractors(EXTRACTORS, globals(), (
    BooruTagExtractor,
    BooruPoolExtractor,
    BooruPostExtractor,
))
