# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34.us/"""

from .booru import BooruExtractor
from .. import text
import collections
import re


class Rule34usExtractor(BooruExtractor):
    category = "rule34us"
    root = "https://rule34.us"
    per_page = 42

    def _init(self):
        self._find_tags = re.compile(
            r'<li class="([^-"]+)-tag"[^>]*><a href="[^;"]+;q=([^"]+)').findall

    def _parse_post(self, post_id):
        url = "{}/index.php?r=posts/view&id={}".format(self.root, post_id)
        page = self.request(url).text
        extr = text.extract_from(page)

        post = {
            "id"      : post_id,
            "tags"    : text.unescape(extr(
                'name="keywords" content="', '"').rstrip(", ")),
            "uploader": text.extract(extr('Added by: ', '</li>'), ">", "<")[0],
            "score"   : text.extract(extr('Score: ', '> - <'), ">", "<")[0],
            "width"   : extr('Size: ', 'w'),
            "height"  : extr(' x ', 'h'),
            "file_url": extr('<source src="', '"') or extr('<img src="', '"'),
        }

        url = post["file_url"]
        if "//video-cdn1." in url:
            post["_fallback"] = (url.replace("//video-cdn1.", "//video."),)
        post["md5"] = url.rpartition("/")[2].partition(".")[0]

        tags = collections.defaultdict(list)
        for tag_type, tag_name in self._find_tags(page):
            tags[tag_type].append(text.unquote(tag_name))
        for key, value in tags.items():
            post["tags_" + key] = " ".join(value)

        return post


class Rule34usTagExtractor(Rule34usExtractor):
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = r"(?:https?://)?rule34\.us/index\.php\?r=posts/index&q=([^&#]+)"
    example = "https://rule34.us/index.php?r=posts/index&q=TAG"

    def __init__(self, match):
        Rule34usExtractor.__init__(self, match)
        self.tags = text.unquote(match.group(1).replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        url = self.root + "/index.php"
        params = {
            "r"   : "posts/index",
            "q"   : self.tags,
            "page": self.page_start,
        }

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for post_id in text.extract_iter(page, '><a id="', '"'):
                yield self._parse_post(post_id)
                cnt += 1

            if cnt < self.per_page:
                return

            if "page" in params:
                del params["page"]
            params["q"] = self.tags + " id:<" + post_id


class Rule34usPostExtractor(Rule34usExtractor):
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?rule34\.us/index\.php\?r=posts/view&id=(\d+)"
    example = "https://rule34.us/index.php?r=posts/view&id=12345"

    def __init__(self, match):
        Rule34usExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self._parse_post(self.post_id),)
