# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://giantessbooru.com/"""

from . import shimmie2
from .. import text

BASE_PATTERN = r"(?:https?://)?giantessbooru\.com/(?:index\.php\?q=/?)?"


class GiantessbooruExtractor(shimmie2.Shimmie2Extractor):
    """Base class for giantessbooru extractors"""
    category = "giantessbooru"
    root = "https://giantessbooru.com"

    def _init(self):
        self.cookies.set("agreed", "true", domain="giantessbooru.com")


class GiantessbooruTagExtractor(GiantessbooruExtractor):
    """Extractor for giantessbooru posts by tag search"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    pattern = BASE_PATTERN + r"post/list/([^/?#]+)(?:/(\d+))?"
    test = (
        ("https://giantessbooru.com/index.php?q=/post/list/drawing/1", {
            "pattern": r"https://giantessbooru\.com/index\.php"
                       r"\?q=/image/\d+\.jpg",
            "range": "1-100",
            "count": 100,
        }),
        ("https://giantessbooru.com/post/list/drawing/1"),
    )

    def __init__(self, match):
        GiantessbooruExtractor.__init__(self, match)
        self.tags, self.page = match.groups()

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        pnum = text.parse_int(self.page, 1)
        file_url_fmt = (self.root + "/index.php?q=/image/{}.jpg").format

        while True:
            url = "{}/index.php?q=/post/list/{}/{}".format(
                self.root, self.tags, pnum)
            extr = text.extract_from(self.request(url).text)

            while True:
                pid = extr('href="./index.php?q=/post/view/', '&')
                if not pid:
                    break

                tags, dimensions, size = extr('title="', '"').split(" // ")
                width, _, height = dimensions.partition("x")

                yield {
                    "file_url": file_url_fmt(pid),
                    "id": pid,
                    "md5": "",
                    "tags": tags,
                    "width": width,
                    "height": height,
                    "size": text.parse_bytes(size[:-1]),
                }

            pnum += 1
            if not extr('/{}">{}<'.format(pnum, pnum), ">"):
                return


class GiantessbooruPostExtractor(GiantessbooruExtractor):
    """Extractor for single giantessbooru posts"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"post/view/(\d+)"
    test = (
        ("https://giantessbooru.com/index.php?q=/post/view/41", {
            "pattern": r"https://giantessbooru\.com/index\.php"
                       r"\?q=/image/41\.jpg",
            "content": "79115ed309d1f4e82e7bead6948760e889139c91",
            "keyword": {
                "extension": "jpg",
                "file_url": "https://giantessbooru.com/index.php"
                            "?q=/image/41.jpg",
                "filename": "41",
                "height": 0,
                "id": 41,
                "md5": "",
                "size": 0,
                "tags": "anime bare_midriff color drawing gentle giantess "
                        "karbo looking_at_tinies negeyari outdoors smiling "
                        "snake_girl white_hair",
                "width": 1387,
            },
        }),
        ("https://giantessbooru.com/post/view/41"),
    )

    def __init__(self, match):
        GiantessbooruExtractor.__init__(self, match)
        self.post_id = match.group(1)

    def posts(self):
        url = "{}/index.php?q=/post/view/{}".format(
            self.root, self.post_id)
        extr = text.extract_from(self.request(url).text)

        return ({
            "id"      : self.post_id,
            "tags"    : extr(": ", "<").partition(" - ")[0].rstrip(")"),
            "md5"     : "",
            "file_url": self.root + extr('id="main_image" src=".', '"'),
            "width"   : extr("orig_width =", ";"),
            "height"  : 0,
            "size"    : 0,
        },)
