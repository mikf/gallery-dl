# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract hentai-manga from https://hentaihere.com/"""

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
    pattern = r"(?:https?://)?(?:www\.)?hentaihere\.com/m/S(\d+)/(\d+)"
    test = ("https://hentaihere.com/m/S13812/1/1/", {
        "url": "964b942cf492b3a129d2fe2608abfc475bc99e71",
        "keyword": "cbcee0c0eb178c4b87f06a834085784f8dddad24",
    })

    def __init__(self, match):
        self.manga_id, self.chapter = match.groups()
        url = "{}/m/S{}/{}/1".format(self.root, self.manga_id, self.chapter)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        title = text.extract(page, "<title>", "</title>")[0]
        chapter_id = text.extract(page, 'report/C', '"')[0]
        pattern = r"Page 1 \| (.+) \(([^)]+)\) - Chapter \d+: (.+) by (.+) at "
        match = re.match(pattern, title)
        return {
            "manga": match.group(1),
            "manga_id": text.parse_int(self.manga_id),
            "chapter": text.parse_int(self.chapter),
            "chapter_id": text.parse_int(chapter_id),
            "type": match.group(2),
            "title": match.group(3),
            "author": match.group(4),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def images(page):
        images = text.extract(page, "var rff_imageList = ", ";")[0]
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
            "keyword": "13c1ce7e15cbb941f01c843b0e89adc993d939ac",
        }),
        ("https://hentaihere.com/m/S7608", {
            "url": "6c5239758dc93f6b1b4175922836c10391b174f7",
            "keyword": "675c7b7a4fa52cf569c283553bd16b4200a5cd36",
        }),
    )

    def chapters(self, page):
        results = []
        manga_id = text.parse_int(
            self.manga_url.rstrip("/").rpartition("/")[2][1:])
        manga, pos = text.extract(
            page, '<span itemprop="name">', '</span>')
        mtype, pos = text.extract(
            page, '<span class="mngType text-danger">[', ']</span>', pos)

        while True:
            marker, pos = text.extract(
                page, '<li class="sub-chp clearfix">', '', pos)
            if marker is None:
                return results
            url, pos = text.extract(page, '<a href="', '"', pos)
            chapter, pos = text.extract(page, 'title="Tagged: -">\n', '<', pos)
            chapter_id, pos = text.extract(page, '/C', '"', pos)
            chapter, _, title = text.unescape(chapter).strip().partition(" - ")
            results.append((url, {
                "manga_id": manga_id, "manga": manga, "type": mtype,
                "chapter_id": text.parse_int(chapter_id),
                "chapter": text.parse_int(chapter),
                "title": title, "lang": "en", "language": "English",
            }))
