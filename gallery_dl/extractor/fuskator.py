# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
    pattern = r"(?:https?://)?fuskator\.com/(?:thumbs|expanded)/([^/?#]+)"
    example = "https://fuskator.com/thumbs/ID/"

    def __init__(self, match):
        self.gallery_hash = match.group(1)
        url = "{}/thumbs/{}/index.html".format(self.root, self.gallery_hash)
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

        title = text.extr(page, "<title>", "</title>").strip()
        title, _, gallery_id = title.rpartition("#")

        return {
            "gallery_id"  : text.parse_int(gallery_id),
            "gallery_hash": self.gallery_hash,
            "title"       : text.unescape(title[:-15]),
            "views"       : data.get("hits"),
            "score"       : data.get("rating"),
            "tags"        : (data.get("tags") or "").split(","),
        }

    def images(self, page):
        return [
            ("https:" + image["imageUrl"], image)
            for image in self.data["images"]
        ]


class FuskatorSearchExtractor(Extractor):
    """Extractor for search results on fuskator.com"""
    category = "fuskator"
    subcategory = "search"
    root = "https://fuskator.com"
    pattern = r"(?:https?://)?fuskator\.com(/(?:search|page)/.+)"
    example = "https://fuskator.com/search/TAG/"

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

            pages = text.extr(page, 'class="pages"><span>', '>&gt;&gt;<')
            if not pages:
                return
            url = self.root + text.rextract(pages, 'href="', '"')[0]
