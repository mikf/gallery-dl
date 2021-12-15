# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://rule34.us/"""

from .booru import BooruExtractor
from .. import text
import re
import collections


class Rule34usExtractor(BooruExtractor):
    category = "rule34us"
    root = "https://rule34.us"
    per_page = 42

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
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
            "file_url": extr(' src="', '"'),
        }
        post["md5"] = post["file_url"].rpartition("/")[2].partition(".")[0]

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
    test = ("https://rule34.us/index.php?r=posts/index&q=[terios]_elysion", {
        "pattern": r"https://img\d*\.rule34\.us"
                   r"/images/../../[0-9a-f]{32}\.\w+",
        "count": 10,
    })

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
    test = (
        ("https://rule34.us/index.php?r=posts/view&id=3709005", {
            "pattern": r"https://img\d*\.rule34\.us/images/14/7b"
                       r"/147bee6fc2e13f73f5f9bac9d4930b13\.png",
            "content": "d714342ea84050f82dda5f0c194d677337abafc5",
        }),
        ("https://rule34.us/index.php?r=posts/view&id=4576310", {
            "pattern": r"https://video\.rule34\.us/images/a2/94"
                       r"/a294ff8e1f8e0efa041e5dc9d1480011\.mp4",
            "keyword": {
                "extension": "mp4",
                "file_url": str,
                "filename": "a294ff8e1f8e0efa041e5dc9d1480011",
                "height": "3982",
                "id": "4576310",
                "md5": "a294ff8e1f8e0efa041e5dc9d1480011",
                "score": r"re:\d+",
                "tags": "tagme, video",
                "tags_general": "video",
                "tags_metadata": "tagme",
                "uploader": "Anonymous",
                "width": "3184",
            },
        }),
    )

    def __init__(self, match):
        Rule34usExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        return (self._parse_post(self.post_id),)
