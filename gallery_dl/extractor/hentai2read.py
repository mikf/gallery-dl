# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://hentai2read.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
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
            page, '<span itemprop="name">', '</span>')
        mtype, pos = text.extract(
            page, '<small class="text-danger">[', ']</small>', pos)
        manga_id = text.parse_int(text.extract(
            page, 'data-mid="', '"', pos)[0])

        while True:
            chapter_id, pos = text.extract(page, ' data-cid="', '"', pos)
            if not chapter_id:
                return results
            _  , pos = text.extract(page, ' href="', '"', pos)
            url, pos = text.extract(page, ' href="', '"', pos)
            chapter, pos = text.extract(page, '>', '<', pos)

            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            results.append((url, {
                "manga_id": manga_id, "manga": manga, "type": mtype,
                "chapter_id": text.parse_int(chapter_id),
                "chapter": text.parse_int(chapter),
                "title": title, "lang": "en", "language": "English",
            }))


class Hentai2readChapterExtractor(ChapterExtractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    category = "hentai2read"
    archive_fmt = "{chapter_id}_{page}"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
        "keyword": "9845105898d28c6a540cffdea60a1a20fab52431",
    })]

    def __init__(self, match):
        url_title, self.chapter = match.groups()
        url = "https://hentai2read.com/{}/{}/".format(url_title, self.chapter)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        title, pos = text.extract(page, "<title>", "</title>")
        manga_id, pos = text.extract(page, 'data-mid="', '"', pos)
        chapter_id, pos = text.extract(page, 'data-cid="', '"', pos)
        match = re.match(r"Reading (.+) \(([^)]+)\) Hentai(?: by (.+))? - "
                         r"(\d+): (.+) . Page 1 ", title)
        return {
            "manga": match.group(1),
            "manga_id": text.parse_int(manga_id),
            "chapter": text.parse_int(self.chapter),
            "chapter_id": text.parse_int(chapter_id),
            "type": match.group(2),
            "author": match.group(3),
            "title": match.group(5),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_images(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "'images' : ", ",\n")[0]
        return [
            ("https://hentaicdn.com/hentai" + part, None)
            for part in json.loads(images)
        ]
