# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann & Instface
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://scatbooru.co.uk/"""

from . import gelbooru_v01
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?scatbooru\.co\.uk"


class ScatbooruExtractor(gelbooru_v01.GelbooruV01Extractor):
    """Base class for scatbooru extractors"""
    category = "scatbooru"
    root = "https://scatbooru.co.uk"

    def _parse_post(self, post_id):
        url = f"{self.root}/?page=post&s=view&id={post_id}"
        extr = text.extract_from(self.request(url).text)

        post = {
            "id"        : post_id,
            "width"     : extr('>Size:&nbsp;', 'x'),
            "height"    : extr('', ' ('),
            "size"      : extr('', ')'),
            "rating"    : (extr('>Rating:&nbsp;', '<') or "?")[0].lower(),
            "source"    : text.extr(extr('>Source:&nbsp;', '>'), 'ref="', '"'),
            "score"     : extr('<a id="psc', '<').rpartition(">")[2],
            "file_url"  : extr('<img alt="img" src="', '"'),
            "date"      : self.parse_datetime_iso(extr('>Posted on ', ' by ')),
            "uploader"  : extr('">', '<'),
            "tags"      : text.unescape(extr(
                'id="tags" name="tags" cols="40" rows="5">', '<')),
        }

        url = post["file_url"]
        post["md5"] = url[url.rfind("/")+1:url.rfind(".")]
        return post


class ScatbooruTagExtractor(ScatbooruExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/\?page=post&s=list&tags=([^&#]+)"
    example = "https://scatbooru.co.uk/?page=post&s=list&tags=TAG"

    def metadata(self):
        self.tags = tags = self.groups[-1]
        return {"search_tags": text.unquote(tags.replace("+", " "))}

    def posts(self):
        url = f"{self.root}/?page=post&s=list&tags={self.tags}&pid="
        return self._pagination(url, '"><a id="p', '"')


class ScatbooruFavoriteExtractor(ScatbooruExtractor):
    subcategory = "favorite"
    directory_fmt = ("{category}", "favorites", "{favorite_id}")
    archive_fmt = "f_{favorite_id}_{id}"
    per_page = 50
    pattern = BASE_PATTERN + r"/\?page=favorites&s=view&id=(\d+)"
    example = "https://scatbooru.co.uk/?page=favorites&s=view&id=1"

    def metadata(self):
        self.favorite_id = fav_id = self.groups[-1]
        return {"favorite_id": text.parse_int(fav_id)}

    def posts(self):
        url = (f"{self.root}/"
               f"?page=favorites&s=view&id={self.favorite_id}&pid=")
        return self._pagination(url, "posts[", "]")


class ScatbooruPostExtractor(ScatbooruExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/\?page=post&s=view&id=(\d+)"
    example = "https://scatbooru.co.uk/?page=post&s=view&id=12345"

    def posts(self):
        return (self._parse_post(self.groups[-1]),)
