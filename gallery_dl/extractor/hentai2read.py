# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentaimanga from https://hentai2read.com/"""

from .. import text
from . import hentaicdn
import re


class Hentai2readMangaExtractor(hentaicdn.HentaicdnMangaExtractor):
    """Extractor for mangas from hentai2read.com"""
    category = "hentai2read"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/?$"]
    test = [
        ("http://hentai2read.com/amazon_elixir/", {
            "url": "d1f87b71d3c97b49a478cdfb6ae96b2d9520ab78",
        }),
        ("http://hentai2read.com/oshikage_riot/", {
            "url": "672f34cce7bf5a855c6c38e8bc9c5117a4b3061c",
        })
    ]

    def __init__(self, match):
        hentaicdn.HentaicdnMangaExtractor.__init__(self)
        self.url_title = match.group(1)

    def get_chapters(self):
        page = text.extract(
            self.request("http://hentai2read.com/" + self.url_title).text,
            '<ul class="nav-chapters remove-margin-b">', '</ul>\n</div>'
        )[0]
        return text.extract_iter(page, '<li>\n<a href="', '"')


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
        self.url_title, self.chapter = match.groups()
        self.url = "http://hentai2read.com/{}/{}/".format(
            self.url_title, self.chapter
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
