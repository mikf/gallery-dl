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
    scheme = "https"
    pattern = [r"(?:https?://)?(?:www\.)?(hentai2read\.com/[^/]+/?)$"]
    test = [
        ("http://hentai2read.com/amazon_elixir/", {
            "url": "273073752d418ec887d7f7211e42b832e8c403ba",
        }),
        ("http://hentai2read.com/oshikage_riot/", {
            "url": "6595f920a3088a15c2819c502862d45f8eb6bea6",
        }),
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
        "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
        "keyword": "fc79e4c70d61ae476aea2b63a75324e3d96f4497",
    })]

    def __init__(self, match):
        hentaicdn.HentaicdnChapterExtractor.__init__(self)
        url_title, self.chapter = match.groups()
        self.url = "https://hentai2read.com/{}/{}/".format(
            url_title, self.chapter
        )

    def get_job_metadata(self, page, images):
        title = text.extract(page, "<title>", "</title>")[0]
        match = re.match(r"Reading (.+) \(([^)]+)\) Hentai(?: by (.+))? - "
                         r"(\d+): (.+) . Page 1 ", title)
        return {
            "manga-id": images[0].split("/")[-3],
            "chapter": self.chapter,
            "count": len(images),
            "manga": match.group(1),
            "type": match.group(2),
            "author": match.group(3),
            "title": match.group(5),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "'images' : ", ",\n")[0]
        return json.loads(images)
