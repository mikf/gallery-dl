# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://realbooru.com/"""

from . import booru
from .. import text, util
import collections
import re

BASE_PATTERN = r"(?:https?://)?realbooru\.com"


class RealbooruExtractor(booru.BooruExtractor):
    basecategory = "booru"
    category = "realbooru"
    root = "https://realbooru.com"

    def _parse_post(self, post_id):
        url = "{}/index.php?page=post&s=view&id={}".format(
            self.root, post_id)
        page = self.request(url).text
        extr = text.extract_from(page)
        rating = extr('name="rating" content="', '"')
        extr('class="container"', '>')

        post = {
            "_html"     : page,
            "id"        : post_id,
            "rating"    : "e" if rating == "adult" else (rating or "?")[0],
            "tags"      : text.unescape(extr(' alt="', '"')),
            "file_url"  : extr('src="', '"'),
            "created_at": extr(">Posted at ", " by "),
            "uploader"  : extr(">", "<"),
            "score"     : extr('">', "<"),
            "title"     : extr('id="title" style="width: 100%;" value="', '"'),
            "source"    : extr('d="source" style="width: 100%;" value="', '"'),
        }

        post["md5"] = post["file_url"].rpartition("/")[2].partition(".")[0]
        return post

    def skip(self, num):
        self.page_start += num
        return num

    def _prepare(self, post):
        post["date"] = text.parse_datetime(post["created_at"], "%b, %d %Y")

    def _pagination(self, params, begin, end):
        url = self.root + "/index.php"
        params["pid"] = self.page_start

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for post_id in text.extract_iter(page, begin, end):
                cnt += 1
                yield self._parse_post(post_id)

            if cnt < self.per_page:
                return
            params["pid"] += self.per_page

    def _tags(self, post, _):
        page = post["_html"]
        tag_container = text.extr(page, 'id="tagLink"', '</div>')
        tags = collections.defaultdict(list)
        pattern = re.compile(
            r'<a class="(?:tag-type-)?([^"]+).*?;tags=([^"&]+)')
        for tag_type, tag_name in pattern.findall(tag_container):
            tags[tag_type].append(text.unescape(text.unquote(tag_name)))
        for key, value in tags.items():
            post["tags_" + key] = " ".join(value)


class RealbooruTagExtractor(RealbooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    per_page = 42
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]*)"
    example = "https://realbooru.com/index.php?page=post&s=list&tags=TAG"

    def metadata(self):
        self.tags = text.unquote(self.groups[0].replace("+", " "))
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination({
            "page": "post",
            "s"   : "list",
            "tags": self.tags,
        }, '<a id="p', '"')


class RealbooruFavoriteExtractor(RealbooruExtractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "favorites", "{favorite_id}")
    archive_fmt = "f_{favorite_id}_{id}"
    per_page = 50
    pattern = BASE_PATTERN + r"/index\.php\?page=favorites&s=view&id=(\d+)"
    example = "https://realbooru.com/index.php?page=favorites&s=view&id=12345"

    def metadata(self):
        return {"favorite_id": text.parse_int(self.groups[0])}

    def posts(self):
        return self._pagination({
            "page": "favorites",
            "s"   : "view",
            "id"  : self.groups[0],
        }, '" id="p', '"')


class RealbooruPoolExtractor(RealbooruExtractor):
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool} {pool_name}")
    archive_fmt = "p_{pool}_{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=pool&s=show&id=(\d+)"
    example = "https://realbooru.com/index.php?page=pool&s=show&id=12345"

    def metadata(self):
        pool_id = self.groups[0]
        url = "{}/index.php?page=pool&s=show&id={}".format(self.root, pool_id)
        page = self.request(url).text

        name, pos = text.extract(page, "<h4>Pool: ", "</h4>")
        self.post_ids = text.extract_iter(
            page, 'class="thumb" id="p', '"', pos)

        return {
            "pool": text.parse_int(pool_id),
            "pool_name": text.unescape(name),
        }

    def posts(self):
        return map(
            self._parse_post,
            util.advance(self.post_ids, self.page_start)
        )


class RealbooruPostExtractor(RealbooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=view&id=(\d+)"
    example = "https://realbooru.com/index.php?page=post&s=view&id=12345"

    def posts(self):
        return (self._parse_post(self.groups[0]),)
