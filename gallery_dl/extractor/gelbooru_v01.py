# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Gelbooru Beta 0.1.11 sites"""

from . import booru
from .. import text


class GelbooruV01Extractor(booru.BooruExtractor):
    basecategory = "gelbooru_v01"
    per_page = 20

    def _parse_post(self, post_id):
        url = f"{self.root}/index.php?page=post&s=view&id={post_id}"
        extr = text.extract_from(self.request(url).text)

        post = {
            "id"        : post_id,
            "created_at": extr('Posted: ', ' <'),
            "uploader"  : extr('By: ', ' <'),
            "width"     : extr('Size: ', 'x'),
            "height"    : extr('', ' <'),
            "source"    : extr('Source: ', ' <'),
            "rating"    : (extr('Rating: ', '<') or "?")[0].lower(),
            "score"     : extr('Score: ', ' <'),
            "file_url"  : extr('<img alt="img" src="', '"'),
            "tags"      : text.unescape(extr(
                'id="tags" name="tags" cols="40" rows="5">', '<')),
        }

        post["md5"] = post["file_url"].rpartition("/")[2].partition(".")[0]
        post["date"] = self.parse_datetime_iso(post["created_at"])

        return post

    def skip(self, num):
        self.page_start += num
        return num

    def _pagination(self, url, begin, end):
        pid = self.page_start

        while True:
            page = self.request(url + str(pid)).text

            cnt = 0
            for post_id in text.extract_iter(page, begin, end):
                yield self._parse_post(post_id)
                cnt += 1

            if cnt < self.per_page:
                return
            pid += self.per_page


BASE_PATTERN = GelbooruV01Extractor.update({
    "thecollection": {
        "root": "https://the-collection.booru.org",
        "pattern": r"the-collection\.booru\.org",
    },
    "illusioncardsbooru": {
        "root": "https://illusioncards.booru.org",
        "pattern": r"illusioncards\.booru\.org",
    },
    "allgirlbooru": {
        "root": "https://allgirl.booru.org",
        "pattern": r"allgirl\.booru\.org",
    },
    "drawfriends": {
        "root": "https://drawfriends.booru.org",
        "pattern": r"drawfriends\.booru\.org",
    },
    "vidyart2": {
        "root": "https://vidyart2.booru.org",
        "pattern": r"vidyart2\.booru\.org",
    },
})


class GelbooruV01TagExtractor(GelbooruV01Extractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = rf"{BASE_PATTERN}/index\.php\?page=post&s=list&tags=([^&#]+)"
    example = "https://allgirl.booru.org/index.php?page=post&s=list&tags=TAG"

    def metadata(self):
        self.tags = tags = self.groups[-1]
        return {"search_tags": text.unquote(tags.replace("+", " "))}

    def posts(self):
        url = f"{self.root}/index.php?page=post&s=list&tags={self.tags}&pid="
        return self._pagination(url, 'class="thumb"><a id="p', '"')


class GelbooruV01FavoriteExtractor(GelbooruV01Extractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "favorites", "{favorite_id}")
    archive_fmt = "f_{favorite_id}_{id}"
    per_page = 50
    pattern = rf"{BASE_PATTERN}/index\.php\?page=favorites&s=view&id=(\d+)"
    example = "https://allgirl.booru.org/index.php?page=favorites&s=view&id=1"

    def metadata(self):
        self.favorite_id = fav_id = self.groups[-1]
        return {"favorite_id": text.parse_int(fav_id)}

    def posts(self):
        url = (f"{self.root}/index.php"
               f"?page=favorites&s=view&id={self.favorite_id}&pid=")
        return self._pagination(url, "posts[", "]")


class GelbooruV01PostExtractor(GelbooruV01Extractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = rf"{BASE_PATTERN}/index\.php\?page=post&s=view&id=(\d+)"
    example = "https://allgirl.booru.org/index.php?page=post&s=view&id=12345"

    def posts(self):
        return (self._parse_post(self.groups[-1]),)
