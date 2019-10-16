# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fuskator.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
import time


class FuskatorGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on fuskator.com"""
    category = "fuskator"
    root = "https://fuskator.com"
    pattern = r"(?:https?://)?fuskator\.com/(?:thumbs|expanded)/([^/?&#]+)"
    test = (
        ("https://fuskator.com/thumbs/d0GnIzXrSKU/", {
            "pattern": r"https://i\d+.fuskator.com/large/d0GnIzXrSKU/.+\.jpg",
            "count": 22,
            "keyword": {
                "gallery_id": 473023,
                "gallery_hash": "d0GnIzXrSKU",
                "title": "re:Shaved Brunette Babe Maria Ryabushkina with ",
                "views": int,
                "score": float,
                "count": 22,
                "tags": list,
            },
        }),
        ("https://fuskator.com/expanded/gXpKzjgIidA/index.html"),
    )

    def __init__(self, match):
        self.gallery_hash = match.group(1)
        url = "{}/thumbs/{}/".format(self.root, self.gallery_hash)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        headers = {
            "Referer"         : self.gallery_url,
            "X-Requested-With": "XMLHttpRequest",
        }
        auth = self.request(
            self.root + "/ajax/auth.aspx", method="POST", headers=headers,
        ).text

        params = {
            "X-Auth": auth,
            "hash"  : self.gallery_hash,
            "_"     : int(time.time()),
        }
        self.data = data = self.request(
            self.root + "/ajax/gal.aspx", params=params, headers=headers,
        ).json()

        title = text.extract(page, "<title>", "</title>")[0].strip()
        title, _, gallery_id = title.rpartition("#")

        return {
            "gallery_id"  : text.parse_int(gallery_id),
            "gallery_hash": self.gallery_hash,
            "title"       : text.unescape(title[:-15]),
            "views"       : data["hits"],
            "score"       : data["rating"],
            "tags"        : data["tags"].split(","),
            "count"       : len(data["images"]),
        }

    def images(self, page):
        for image in self.data["images"]:
            yield "https:" + image["imageUrl"], image


class FuskatorSearchExtractor(Extractor):
    """Extractor for search results on fuskator.com"""
    category = "fuskator"
    subcategory = "search"
    root = "https://fuskator.com"
    pattern = r"(?:https?://)?fuskator\.com(/(?:search|page)/.+)"
    test = (
        ("https://fuskator.com/search/red_swimsuit/", {
            "pattern": FuskatorGalleryExtractor.pattern,
            "count": ">= 40",
        }),
        ("https://fuskator.com/page/3/swimsuit/quality/"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def items(self):
        url = self.root + self.path
        data = {"_extractor": FuskatorGalleryExtractor}

        while True:
            page = self.request(url).text
            for path in text.extract_iter(
                    page, 'class="pic_pad"><a href="', '"'):
                yield Message.Queue, self.root + path, data

            pages = text.extract(page, 'class="pages"><span>', '>&gt;&gt;<')[0]
            if not pages:
                return
            url = self.root + text.rextract(pages, 'href="', '"')[0]
