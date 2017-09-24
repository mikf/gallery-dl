# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://hentai2read.com/"""

from .common import MangaExtractor
from .. import text, util
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
            "keyword": "13c1ce7e15cbb941f01c843b0e89adc993d939ac",
        }),
        ("http://hentai2read.com/oshikage_riot/", {
            "url": "6595f920a3088a15c2819c502862d45f8eb6bea6",
            "keyword": "675c7b7a4fa52cf569c283553bd16b4200a5cd36",
        }),
    ]

    def chapters(self, page):
        results = []
        manga, pos = text.extract(
            page, '<span itemprop="itemreviewed">', '</span>')
        mtype, pos = text.extract(
            page, '<small class="text-danger">[', ']</small>', pos)
        manga_id = util.safe_int(text.extract(page, 'data-mid="', '"', pos)[0])
        page, pos = text.extract(
            page, '<ul class="nav-chapters remove-margin-b">', '</ul>\n</div>')

        pos = 0
        while True:
            url, pos = text.extract(page, '<li>\n<a href="', '"', pos)
            if not url:
                return results
            chapter_id, pos = text.extract(page, 'data-cid="', '"', pos)
            chapter, pos = text.extract(page, '\n', '<', pos)
            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            results.append((url, {
                "manga_id": manga_id, "manga": manga, "type": mtype,
                "chapter_id": util.safe_int(chapter_id),
                "chapter": util.safe_int(chapter),
                "title": title, "lang": "en", "language": "English",
            }))


class Hentai2readChapterExtractor(hentaicdn.HentaicdnChapterExtractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    category = "hentai2read"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
        "keyword": "0f6408d462a14bfe58030117dc295b84666843d0",
    })]

    def __init__(self, match):
        hentaicdn.HentaicdnChapterExtractor.__init__(self)
        url_title, self.chapter = match.groups()
        self.url = "https://hentai2read.com/{}/{}/".format(
            url_title, self.chapter
        )

    def get_job_metadata(self, page, images):
        title = text.extract(page, "<title>", "</title>")[0]
        chapter_id = text.extract(page, 'data-cid="', '"')[0]
        match = re.match(r"Reading (.+) \(([^)]+)\) Hentai(?: by (.+))? - "
                         r"(\d+): (.+) . Page 1 ", title)
        return {
            "manga_id": images[0].split("/")[-3],
            "manga": match.group(1),
            "type": match.group(2),
            "chapter_id": chapter_id,
            "chapter": self.chapter,
            "author": match.group(3),
            "title": match.group(5),
            "count": len(images),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "'images' : ", ",\n")[0]
        return json.loads(images)
