# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://hentai2read.com/"""

from .common import MangaExtractor
from .. import text
from . import hentaicdn
import re
import json


class Hentai2readMangaExtractor(MangaExtractor):
    """Extractor for hmanga from hentai2read.com"""
    category = "hentai2read"
    pattern = [r"(?:https?://)?(?:www\.)?(hentai2read\.com/[^/]+/?)$"]
    test = [
        ("http://hentai2read.com/amazon_elixir/", {
            "url": "d1f87b71d3c97b49a478cdfb6ae96b2d9520ab78",
        }),
        ("http://hentai2read.com/oshikage_riot/", {
            "url": "672f34cce7bf5a855c6c38e8bc9c5117a4b3061c",
        })
    ]

    def chapters(self, page):
        page = text.extract(
            page, '<ul class="nav-chapters remove-margin-b">', '</ul>\n</div>'
        )[0]
        return list(text.extract_iter(page, '<li>\n<a href="', '"'))


class Hentai2readChapterExtractor(hentaicdn.HentaicdnChapterExtractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    category = "hentai2read"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "fb5fc4d7cc194116960eaa648c7e045a6e6f0c11",
        "keyword": "c05d0d0bbe188926b15a43df1f8f65b8ac11c3fd",
    })]

    def __init__(self, match):
        hentaicdn.HentaicdnChapterExtractor.__init__(self)
        url_title, self.chapter = match.groups()
        self.url = "http://hentai2read.com/{}/{}/".format(
            url_title, self.chapter
        )

    def get_job_metadata(self, page, images):
        title = text.extract(page, "<title>", "</title>")[0]
        match = re.match(r"Reading (?:(.+) dj - )?(.+) Hentai - \d+: ", title)
        return {
            "gallery-id": images[0].split("/")[-3],
            "chapter": self.chapter,
            "count": len(images),
            "series": match.group(1) or "",
            "title": match.group(2),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "'images' : ", ",\n")[0]
        return json.loads(images)
