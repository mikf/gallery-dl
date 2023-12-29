# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
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
        url = "{}/index.php?page=post&s=view&id={}".format(
            self.root, post_id)
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
        post["date"] = text.parse_datetime(
            post["created_at"], "%Y-%m-%d %H:%M:%S")

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
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=list&tags=([^&#]+)"
    example = "https://allgirl.booru.org/index.php?page=post&s=list&tags=TAG"

    def __init__(self, match):
        GelbooruV01Extractor.__init__(self, match)
        self.tags = match.group(match.lastindex)

    def metadata(self):
        return {"search_tags": text.unquote(self.tags.replace("+", " "))}

    def posts(self):
        url = "{}/index.php?page=post&s=list&tags={}&pid=".format(
            self.root, self.tags)
        return self._pagination(url, 'class="thumb"><a id="p', '"')


class GelbooruV01FavoriteExtractor(GelbooruV01Extractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "favorites", "{favorite_id}")
    archive_fmt = "f_{favorite_id}_{id}"
    per_page = 50
    pattern = BASE_PATTERN + r"/index\.php\?page=favorites&s=view&id=(\d+)"
    example = "https://allgirl.booru.org/index.php?page=favorites&s=view&id=1"

    def __init__(self, match):
        GelbooruV01Extractor.__init__(self, match)
        self.favorite_id = match.group(match.lastindex)

    def metadata(self):
        return {"favorite_id": text.parse_int(self.favorite_id)}

    def posts(self):
        url = "{}/index.php?page=favorites&s=view&id={}&pid=".format(
            self.root, self.favorite_id)
        return self._pagination(url, "posts[", "]")


class GelbooruV01PostExtractor(GelbooruV01Extractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/index\.php\?page=post&s=view&id=(\d+)"
    example = "https://allgirl.booru.org/index.php?page=post&s=view&id=12345"

    def __init__(self, match):
        GelbooruV01Extractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        return (self._parse_post(self.post_id),)
