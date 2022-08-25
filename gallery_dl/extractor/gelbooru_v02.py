# -*- coding: utf-8 -*-

# Copyright 2021-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Gelbooru Beta 0.2 sites"""

from . import booru
from .. import text, util, exception

from xml.etree import ElementTree
import collections
import re


class GelbooruV02Extractor(booru.BooruExtractor):
    basecategory = "gelbooru_v02"

    def __init__(self, match):
        booru.BooruExtractor.__init__(self, match)
        self.api_key = self.config("api-key")
        self.user_id = self.config("user-id")

        try:
            self.api_root = INSTANCES[self.category]["api_root"]
        except KeyError:
            self.api_root = self.root

        if self.category == "realbooru":
            self._file_url = self._file_url_realbooru

    def _api_request(self, params):
        url = self.api_root + "/index.php?page=dapi&s=post&q=index"
        return ElementTree.fromstring(self.request(url, params=params).text)

    def _pagination(self, params):
        params["pid"] = self.page_start
        params["limit"] = self.per_page

        post = None
        while True:
            try:
                root = self._api_request(params)
            except ElementTree.ParseError:
                if "tags" not in params or post is None:
                    raise
                taglist = [tag for tag in params["tags"].split()
                           if not tag.startswith("id:<")]
                taglist.append("id:<" + str(post.attrib["id"]))
                params["tags"] = " ".join(taglist)
                params["pid"] = 0
                continue

            post = None
            for post in root:
                yield post.attrib

            if len(root) < self.per_page:
                return
            params["pid"] += 1

    def _pagination_html(self, params):
        url = self.root + "/index.php"
        params["pid"] = self.page_start * self.per_page

        data = {}
        while True:
            num_ids = 0
            page = self.request(url, params=params).text

            for data["id"] in text.extract_iter(page, '" id="p', '"'):
                num_ids += 1
                for post in self._api_request(data):
                    yield post.attrib

            if num_ids < self.per_page:
                return
            params["pid"] += self.per_page

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(
            post["created_at"], "%a %b %d %H:%M:%S %z %Y")

    def _file_url_realbooru(self, post):
        url = post["file_url"]
        if url.count("/") == 5:
            md5 = post["md5"]
            url = "{}/images/{}/{}/{}.{}".format(
                self.root, md5[0:2], md5[2:4], md5, url.rpartition(".")[2])
        return url

    def _extended_tags(self, post, page=None):
        if not page:
            url = "{}/index.php?page=post&s=view&id={}".format(
                self.root, post["id"])
            page = self.request(url).text
        html = text.extract(page, '<ul id="tag-', '</ul>')[0]
        if not html:
            html = text.extract(page, '<ul class="tag-', '</ul>')[0]
        if html:
            tags = collections.defaultdict(list)
            pattern = re.compile(
                r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'&]+)", re.S)
            for tag_type, tag_name in pattern.findall(html):
                tags[tag_type].append(text.unquote(tag_name))
            for key, value in tags.items():
                post["tags_" + key] = " ".join(value)
        return page

    def _notes(self, post, page=None):
        if not page:
            url = "{}/index.php?page=post&s=view&id={}".format(
                self.root, post["id"])
            page = self.request(url).text
        notes = []
        notes_data = text.extract(page, '<section id="notes"', '</section>')[0]
        if not notes_data:
            return

        note_iter = text.extract_iter(notes_data, '<article', '</article>')
        extr = text.extract
        for note_data in note_iter:
            note = {
                "width": int(extr(note_data, 'data-width="', '"')[0]),
                "height": int(extr(note_data, 'data-height="', '"')[0]),
                "x": int(extr(note_data, 'data-x="', '"')[0]),
                "y": int(extr(note_data, 'data-y="', '"')[0]),
                "body": extr(note_data, 'data-body="', '"')[0],
            }
            notes.append(note)

        post["notes"] = notes


INSTANCES = {
    "realbooru": {
        "root": "https://realbooru.com",
        "pattern": r"realbooru\.com",
    },
    "rule34": {
        "root": "https://rule34.xxx",
        "pattern": r"rule34\.xxx",
        "api_root": "https://api.rule34.xxx",
    },
    "safebooru": {
        "root": "https://safebooru.org",
        "pattern": r"safebooru\.org",
    },
    "tbib": {
        "root": "https://tbib.org",
        "pattern": r"tbib\.org",
    },
    "hypnohub": {
        "root": "https://hypnohub.net",
        "pattern": r"hypnohub\.net",
    },
}

BASE_PATTERN = GelbooruV02Extractor.update(INSTANCES)


class GelbooruV02TagExtractor(GelbooruV02Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]+)"
    test = (
        ("https://rule34.xxx/index.php?page=post&s=list&tags=danraku", {
            "content": "5c6ae9ee13e6d4bc9cb8bdce224c84e67fbfa36c",
            "pattern": r"https?://.*rule34\.xxx/images/\d+/[0-9a-f]+\.jpg",
            "count": 2,
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
        ("https://hypnohub.net/index.php?page=post&s=list&tags=gonoike_biwa", {
            "url": "fe662b86d38c331fcac9c62af100167d404937dc",
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination({"tags": self.tags})


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
        ("https://hypnohub.net/index.php?page=pool&s=show&id=61", {
            "url": "d314826280073441a2da609f70ee814d1f4b9407",
            "count": 3,
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)

        if self.category == "rule34":
            self.posts = self._posts_pages
            self.per_page = 45
        else:
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

    def _posts_pages(self):
        return self._pagination_html({
            "page": "pool",
            "s"   : "show",
            "id"  : self.pool_id,
        })


class GelbooruV02FavoriteExtractor(GelbooruV02Extractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "favorites", "{favorite_id}")
    archive_fmt = "f_{favorite_id}_{id}"
    per_page = 50
    pattern = BASE_PATTERN + r"/index\.php\?page=favorites&s=view&id=(\d+)"
    test = (
        ("https://rule34.xxx/index.php?page=favorites&s=view&id=1030218", {
            "count": 3,
        }),
        ("https://safebooru.org/index.php?page=favorites&s=view&id=17567", {
            "count": 2,
        }),
        ("https://realbooru.com/index.php?page=favorites&s=view&id=274", {
            "count": 2,
        }),
        ("https://tbib.org/index.php?page=favorites&s=view&id=7881", {
            "count": 3,
        }),
        ("https://hypnohub.net/index.php?page=favorites&s=view&id=43546", {
            "count": 3,
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.favorite_id = match.group(match.lastindex)

    def metadata(self):
        return {"favorite_id": text.parse_int(self.favorite_id)}

    def posts(self):
        return self._pagination_html({
            "page": "favorites",
            "s"   : "view",
            "id"  : self.favorite_id,
        })


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
            "pattern": r"https://realbooru\.com/images/dc/b5"
                       r"/dcb5c0ce9ec0bf74a6930608985f4719\.jpeg",
            "content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",
        }),
        ("https://tbib.org/index.php?page=post&s=view&id=9233957", {
            "url": "5a6ebe07bfff8e6d27f7c30b5480f27abcb577d2",
            "content": "1c3831b6fbaa4686e3c79035b5d98460b1c85c43",
        }),
        ("https://hypnohub.net/index.php?page=post&s=view&id=73964", {
            "pattern": r"https://hypnohub\.net/images/7a/37"
                       r"/7a37c0ba372f35767fb10c904a398831\.png",
            "content": "02d5f5a8396b621a6efc04c5f8ef1b7225dfc6ee",
        }),
    )

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return self._pagination({"id": self.post_id})
