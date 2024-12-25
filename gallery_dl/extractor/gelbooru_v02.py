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

    def _init(self):
        self.api_key = self.config("api-key")
        self.user_id = self.config("user-id")
        self.root_api = self.config_instance("root-api") or self.root

    def _api_request(self, params):
        url = self.root_api + "/index.php?page=dapi&s=post&q=index"
        return ElementTree.fromstring(self.request(url, params=params).text)

    def _pagination(self, params):
        params["pid"] = self.page_start
        params["limit"] = self.per_page

        post = total = None
        count = 0

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

            if total is None:
                try:
                    total = int(root.attrib["count"])
                    self.log.debug("%s posts in total", total)
                except Exception as exc:
                    total = 0
                    self.log.debug(
                        "Failed to get total number of posts (%s: %s)",
                        exc.__class__.__name__, exc)

            post = None
            for post in root:
                yield post.attrib

            num = len(root)
            count += num
            if num < self.per_page:
                if not total or count >= total:
                    return
                if not num:
                    self.log.debug("Empty response - Retrying")
                    continue

            params["pid"] += 1

    def _pagination_html(self, params):
        url = self.root + "/index.php"
        params["pid"] = self.page_start * self.per_page

        data = {}
        find_ids = re.compile(r"\sid=\"p(\d+)").findall

        while True:
            page = self.request(url, params=params).text
            pids = find_ids(page)

            for data["id"] in pids:
                for post in self._api_request(data):
                    yield post.attrib

            if len(pids) < self.per_page:
                return
            params["pid"] += self.per_page

    @staticmethod
    def _prepare(post):
        post["tags"] = post["tags"].strip()
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
            tags[tag_type].append(text.unescape(text.unquote(tag_name)))
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


BASE_PATTERN = GelbooruV02Extractor.update({
    "rule34": {
        "root": "https://rule34.xxx",
        "root-api": "https://api.rule34.xxx",
        "pattern": r"(?:www\.)?rule34\.xxx",
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
    "xbooru": {
        "root": "https://xbooru.com",
        "pattern": r"xbooru\.com",
    },
})


class GelbooruV02TagExtractor(GelbooruV02Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]*)"
    example = "https://safebooru.org/index.php?page=post&s=list&tags=TAG"

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        if self.tags == "all":
            self.tags = ""
        return self._pagination({"tags": self.tags})


class GelbooruV02PoolExtractor(GelbooruV02Extractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=pool&s=show&id=(\d+)"
    example = "https://safebooru.org/index.php?page=pool&s=show&id=12345"

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
    example = "https://safebooru.org/index.php?page=favorites&s=view&id=12345"

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
    example = "https://safebooru.org/index.php?page=post&s=view&id=12345"

    def __init__(self, match):
        GelbooruV02Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return self._pagination({"id": self.post_id})
