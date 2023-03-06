# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai2read.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
import re


class Hentai2readBase():
    """Base class for hentai2read extractors"""
    category = "hentai2read"
    root = "https://hentai2read.com"


class Hentai2readChapterExtractor(Hentai2readBase, ChapterExtractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?hentai2read\.com(/[^/?#]+/([^/?#]+))"
    test = (
        ("https://hentai2read.com/amazon_elixir/1/", {
            "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
            "keyword": "85645b02d34aa11b3deb6dadd7536863476e1bad",
        }),
        ("https://hentai2read.com/popuni_kei_joshi_panic/2.5/", {
            "pattern": r"https://hentaicdn\.com/hentai"
                       r"/13088/2\.5y/ccdn00\d+\.jpg",
            "count": 36,
            "keyword": {
                "author": "Kurisu",
                "chapter": 2,
                "chapter_id": 75152,
                "chapter_minor": ".5",
                "count": 36,
                "lang": "en",
                "language": "English",
                "manga": "Popuni Kei Joshi Panic!",
                "manga_id": 13088,
                "page": int,
                "title": "Popuni Kei Joshi Panic! 2.5",
                "type": "Original",
            },
        }),
    )

    def __init__(self, match):
        self.chapter = match.group(2)
        ChapterExtractor.__init__(self, match)

    def metadata(self, page):
        title, pos = text.extract(page, "<title>", "</title>")
        manga_id, pos = text.extract(page, 'data-mid="', '"', pos)
        chapter_id, pos = text.extract(page, 'data-cid="', '"', pos)
        chapter, sep, minor = self.chapter.partition(".")
        match = re.match(r"Reading (.+) \(([^)]+)\) Hentai(?: by (.+))? - "
                         r"([^:]+): (.+) . Page 1 ", title)
        return {
            "manga": match.group(1),
            "manga_id": text.parse_int(manga_id),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": text.parse_int(chapter_id),
            "type": match.group(2),
            "author": match.group(3),
            "title": match.group(5),
            "lang": "en",
            "language": "English",
        }

    def images(self, page):
        images = text.extract(page, "'images' : ", ",\n")[0]
        return [
            ("https://hentaicdn.com/hentai" + part, None)
            for part in util.json_loads(images)
        ]


class Hentai2readMangaExtractor(Hentai2readBase, MangaExtractor):
    """Extractor for hmanga from hentai2read.com"""
    chapterclass = Hentai2readChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?hentai2read\.com(/[^/?#]+)/?$"
    test = (
        ("https://hentai2read.com/amazon_elixir/", {
            "url": "273073752d418ec887d7f7211e42b832e8c403ba",
            "keyword": "5c1b712258e78e120907121d3987c71f834d13e1",
        }),
        ("https://hentai2read.com/oshikage_riot/", {
            "url": "6595f920a3088a15c2819c502862d45f8eb6bea6",
            "keyword": "a2e9724acb221040d4b29bf9aa8cb75b2240d8af",
        }),
        ("https://hentai2read.com/popuni_kei_joshi_panic/", {
            "pattern": Hentai2readChapterExtractor.pattern,
            "range": "2-3",
            "keyword": {
                "chapter": int,
                "chapter_id": int,
                "chapter_minor": ".5",
                "lang": "en",
                "language": "English",
                "manga": "Popuni Kei Joshi Panic!",
                "manga_id": 13088,
                "title": str,
                "type": "Original",
            },
        }),
    )

    def chapters(self, page):
        results = []

        pos = page.find('itemscope itemtype="http://schema.org/Book') + 1
        manga, pos = text.extract(
            page, '<span itemprop="name">', '</span>', pos)
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
            chapter, sep, minor = chapter.partition(".")

            results.append((url, {
                "manga": manga,
                "manga_id": manga_id,
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(chapter_id),
                "type": mtype,
                "title": title,
                "lang": "en",
                "language": "English",
            }))
