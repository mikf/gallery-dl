# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentaimanga from https://hentaihere.com/"""

from .. import text
from . import hentaicdn
import re

class HentaihereMangaExtractor(hentaicdn.HentaicdnMangaExtractor):
    """Extractor for mangas from hentaihere.com"""
    category = "hentaihere"
    pattern = [r"(?:https?://)?(?:www\.)?hentaihere\.com/m/S(\d+)/?$"]
    test = [
        ("http://hentaihere.com/m/S13812", {
            "url": "167ec26c73c7d01ad8ad0a2b88257a901aa8330e",
        }),
        ("http://hentaihere.com/m/S7608", {
            "url": "17dd982270456ce51ec7189f9e37728ef9f894c8",
        }),
    ]

    def __init__(self, match):
        hentaicdn.HentaicdnMangaExtractor.__init__(self)
        self.gid = match.group(1)

    def get_chapters(self):
        return text.extract_iter(
            self.request("http://hentaihere.com/m/S" + self.gid).text,
            '<li class="sub-chp clearfix">\n<a href="','"'
        )


class HentaihereChapterExtractor(hentaicdn.HentaicdnChapterExtractor):
    """Extractor for a single manga chapter from hentaihere.com"""
    category = "hentaihere"
    pattern = [r"(?:https?://)?(?:www\.)?hentaihere\.com/m/S(\d+)/(\d+)"]
    test = [("http://hentaihere.com/m/S13812/1/1/", {
        "url": "fb5fc4d7cc194116960eaa648c7e045a6e6f0c11",
        "keyword": "e8625ccca8466a5dee089394fc29efea6d6e2950",
    })]

    def __init__(self, match):
        hentaicdn.HentaicdnChapterExtractor.__init__(self)
        self.gid, self.chapter = match.groups()
        self.url = "http://hentaihere.com/m/S{}/{}/1".format(self.gid, self.chapter)

    def get_job_metadata(self, page, images):
        title = text.extract(page, "<title>", "</title>")[0]
        pattern = r"Page 1 \| (.+) \(([^)]+)\) - Chapter \d+: (.+) by (.+) at "
        match = re.match(pattern, title)
        return {
            "gallery-id": self.gid,
            "title": match.group(1),
            "type": match.group(2),
            "chapter": self.chapter,
            "chapter-name": match.group(3),
            "author": match.group(4),
            "count": len(images),
            "lang": "en",
            "language": "English",
        }
