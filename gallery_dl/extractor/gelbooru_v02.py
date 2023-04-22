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
            self.items = self._items_realbooru
            self._tags = self._tags_realbooru

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

    def _html(self, post):
        return self.request("{}/index.php?page=post&s=view&id={}".format(
            self.root, post["id"])).text

    def _tags(self, post, page):
        tag_container = (text.extr(page, '<ul id="tag-', '</ul>') or
                         text.extr(page, '<ul class="tag-', '</ul>'))
        if not tag_container:
            return

        tags = collections.defaultdict(list)
        pattern = re.compile(
            r"tag-type-([^\"' ]+).*?[?;]tags=([^\"'&]+)", re.S)
        for tag_type, tag_name in pattern.findall(tag_container):
            tags[tag_type].append(text.unquote(tag_name))
        for key, value in tags.items():
            post["tags_" + key] = " ".join(value)

    def _notes(self, post, page):
        note_container = text.extr(page, 'id="note-container"', "<img ")
        if not note_container:
            return

        post["notes"] = notes = []
        for note in note_container.split('class="note-box"')[1:]:
            extr = text.extract_from(note)
            notes.append({
                "width" : int(extr("width:", "p")),
                "height": int(extr("height:", "p")),
                "y"     : int(extr("top:", "p")),
                "x"     : int(extr("left:", "p")),
                "id"    : int(extr('id="note-body-', '"')),
                "body"  : text.unescape(text.remove_html(extr(">", "</div>"))),
            })

    def _file_url_realbooru(self, post):
        url = post["file_url"]
        md5 = post["md5"]
        if md5 not in post["preview_url"] or url.count("/") == 5:
            url = "{}/images/{}/{}/{}.{}".format(
                self.root, md5[0:2], md5[2:4], md5, url.rpartition(".")[2])
        return url

    def _items_realbooru(self):
        from .common import Message
        data = self.metadata()

        for post in self.posts():
            try:
                html = self._html(post)
                url = post["file_url"] = text.rextract(
                    html, 'href="', '"', html.index(">Original<"))[0]
            except Exception:
                self.log.debug("Unable to fetch download URL for post %s "
                               "(md5: %s)", post.get("id"), post.get("md5"))
                continue

            text.nameext_from_url(url, post)
            post.update(data)
            self._prepare(post)
            self._tags(post, html)

            yield Message.Directory, post
            yield Message.Url, url, post

    def _tags_realbooru(self, post, page):
        tag_container = text.extr(page, 'id="tagLink"', '</div>')
        tags = collections.defaultdict(list)
        pattern = re.compile(
            r'<a class="(?:tag-type-)?([^"]+).*?;tags=([^"&]+)')
        for tag_type, tag_name in pattern.findall(tag_container):
            tags[tag_type].append(text.unquote(tag_name))
        for key, value in tags.items():
            post["tags_" + key] = " ".join(value)


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
            "content": ("5c6ae9ee13e6d4bc9cb8bdce224c84e67fbfa36c",
                        "622e80be3f496672c44aab5c47fbc6941c61bc79"),
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
        ("https://rule34.xxx/index.php?page=post&s=view&id=863", {
            "pattern": r"https://api-cdn\.rule34\.xxx/images"
                       r"/1/6aafbdb3e22f3f3b412ea2cf53321317a37063f3\.jpg",
            "content": ("a43f418aa350039af0d11cae501396a33bbe2201",
                        "67b516295950867e1c1ab6bc13b35d3b762ed2a3"),
            "options": (("tags", True), ("notes", True)),
            "keyword": {
                "tags_artist": "reverse_noise yamu_(reverse_noise)",
                "tags_character": "hong_meiling",
                "tags_copyright": "touhou",
                "tags_general": str,
                "tags_metadata": "censored translated",
                "notes": [
                    {
                        "body": "It feels angry, I'm losing myself... "
                                "It won't calm down!",
                        "height": 65,
                        "id": 93586,
                        "width": 116,
                        "x": 22,
                        "y": 333,
                    },
                    {
                        "body": "REPUTATION OF RAGE",
                        "height": 272,
                        "id": 93587,
                        "width": 199,
                        "x": 78,
                        "y": 442,
                    },
                ],

            },
        }),
        ("https://hypnohub.net/index.php?page=post&s=view&id=1439", {
            "pattern": r"https://hypnohub\.net/images"
                       r"/90/24/90245c3c5250c2a8173255d3923a010b\.jpg",
            "content": "5987c5d2354f22e5fa9b7ee7ce4a6f7beb8b2b71",
            "options": (("tags", True), ("notes", True)),
            "keyword": {
                "tags_artist": "brokenteapot",
                "tags_character": "hsien-ko",
                "tags_copyright": "capcom darkstalkers",
                "tags_general": str,
                "tags_metadata": "dialogue text translated",
                "notes": [
                    {
                        "body": "Master Master Master "
                                "Master Master Master",
                        "height": 83,
                        "id": 10577,
                        "width": 129,
                        "x": 259,
                        "y": 20,
                    },
                    {
                        "body": "Response Response Response "
                                "Response Response Response",
                        "height": 86,
                        "id": 10578,
                        "width": 125,
                        "x": 126,
                        "y": 20,
                    },
                    {
                        "body": "Obedience Obedience Obedience "
                                "Obedience Obedience Obedience",
                        "height": 80,
                        "id": 10579,
                        "width": 98,
                        "x": 20,
                        "y": 20,
                    },
                ],

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
            "pattern": r"https://realbooru\.com//?images/dc/b5"
                       r"/dcb5c0ce9ec0bf74a6930608985f4719\.jpeg",
            "content": "7f5873ce3b6cd295ea2e81fcb49583098ea9c8da",
            "options": (("tags", True),),
            "keyword": {
                "tags_general": "1girl blonde blonde_hair blue_eyes cute "
                                "female female_only looking_at_viewer smile "
                                "solo solo_female teeth",
                "tags_model": "jennifer_lawrence",
            },
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
