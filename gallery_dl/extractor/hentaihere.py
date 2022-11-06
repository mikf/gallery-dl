# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaihere.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text
import json
import re


class HentaihereBase():
    """Base class for hentaihere extractors"""
    category = "hentaihere"
    root = "https://hentaihere.com"


class HentaihereChapterExtractor(HentaihereBase, ChapterExtractor):
    """Extractor for a single manga chapter from hentaihere.com"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = r"(?:https?://)?(?:www\.)?hentaihere\.com/m/S(\d+)/([^/?#]+)"
    test = (
        ("https://hentaihere.com/m/S13812/1/1/", {
            "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
            "keyword": "0207d20eea3a15d2a8d1496755bdfa49de7cfa9d",
        }),
        ("https://hentaihere.com/m/S23048/1.5/1/", {
            "pattern": r"https://hentaicdn\.com/hentai"
                       r"/23048/1\.5/ccdn00\d+\.jpg",
            "count": 32,
            "keyword": {
                "author": "Shinozuka Yuuji",
                "chapter": 1,
                "chapter_id": 80186,
                "chapter_minor": ".5",
                "count": 32,
                "lang": "en",
                "language": "English",
                "manga": "High School Slut's Love Consultation",
                "manga_id": 23048,
                "page": int,
                "title": "High School Slut's Love Consultation + "
                         "Girlfriend [Full Color]",
                "type": "Original",
            },
        }),
    )

    def __init__(self, match):
        self.manga_id, self.chapter = match.groups()
        url = "{}/m/S{}/{}/1".format(self.root, self.manga_id, self.chapter)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.extr(page, "<title>", "</title>")
        chapter_id = text.extr(page, 'report/C', '"')
        chapter, sep, minor = self.chapter.partition(".")
        pattern = r"Page 1 \| (.+) \(([^)]+)\) - Chapter \d+: (.+) by (.+) at "
        match = re.match(pattern, title)
        return {
            "manga": match.group(1),
            "manga_id": text.parse_int(self.manga_id),
            "chapter": text.parse_int(chapter),
            "chapter_minor": sep + minor,
            "chapter_id": text.parse_int(chapter_id),
            "type": match.group(2),
            "title": match.group(3),
            "author": match.group(4),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def images(page):
        images = text.extr(page, "var rff_imageList = ", ";")
        return [
            ("https://hentaicdn.com/hentai" + part, None)
            for part in json.loads(images)
        ]


class HentaihereMangaExtractor(HentaihereBase, MangaExtractor):
    """Extractor for hmanga from hentaihere.com"""
    chapterclass = HentaihereChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?hentaihere\.com(/m/S\d+)/?$"
    test = (
        ("https://hentaihere.com/m/S13812", {
            "url": "d1ba6e28bb2162e844f8559c2b2725ba0a093559",
            "keyword": "5c1b712258e78e120907121d3987c71f834d13e1",
        }),
        ("https://hentaihere.com/m/S7608", {
            "url": "6c5239758dc93f6b1b4175922836c10391b174f7",
            "keyword": {
                "chapter": int,
                "chapter_id": int,
                "chapter_minor": "",
                "lang": "en",
                "language": "English",
                "manga": "Oshikake Riot",
                "manga_id": 7608,
                "title": r"re:Oshikake Riot( \d+)?",
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
            page, '<span class="mngType text-danger">[', ']</span>', pos)
        manga_id = text.parse_int(
            self.manga_url.rstrip("/").rpartition("/")[2][1:])

        while True:
            marker, pos = text.extract(
                page, '<li class="sub-chp clearfix">', '', pos)
            if marker is None:
                return results
            url, pos = text.extract(page, '<a href="', '"', pos)

            chapter, pos = text.extract(page, 'title="Tagged: -">\n', '<', pos)
            chapter_id, pos = text.extract(page, '/C', '"', pos)
            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            chapter, sep, minor = chapter.partition(".")

            results.append((url, {
                "manga_id": manga_id,
                "manga": manga,
                "chapter": text.parse_int(chapter),
                "chapter_minor": sep + minor,
                "chapter_id": text.parse_int(chapter_id),
                "type": mtype,
                "title": title,
                "lang": "en",
                "language": "English",
            }))
