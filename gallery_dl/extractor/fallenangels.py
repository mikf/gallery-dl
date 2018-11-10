# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://www.fascans.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util
import json


class FallenangelsChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters from fascans.com"""
    category = "fallenangels"
    pattern = [(r"(?:https?://)?(manga|truyen)\.fascans\.com"
                r"/manga/([^/]+)/(\d+)(\.[^/?&#]+)?")]
    test = [
        ("https://manga.fascans.com/manga/chronos-ruler/20/1", {
            "url": "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
            "keyword": "4e1722cf0ed8ee5fc5c64147ac3f39342e767cd8",
        }),
        ("http://truyen.fascans.com/manga/hungry-marie/8", {
            "url": "1f923d9cb337d5e7bbf4323719881794a951c6ae",
            "keyword": "c7beeb7d8a65d5d8ab451f076f584bd4d52b7210",
        }),
        ("http://manga.fascans.com/manga/rakudai-kishi-no-eiyuutan/19.5", {
            "keyword": "bf7dd1c462a80ffe50b92fec00b7acda2f8b800e",
        }),
    ]

    def __init__(self, match):
        self.version, self.manga, self.chapter, self.minor = match.groups()
        url = "https://{}.fascans.com/manga/{}/{}/1".format(
            self.version, self.manga, self.chapter)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        lang = "vi" if self.version == "truyen" else "en"
        data = {
            "chapter": self.chapter,
            "chapter_minor": self.minor or "",
            "lang": lang,
            "language": util.code_to_language(lang),
        }
        return text.extract_all(page, (
            ("manga", 'name="description" content="', ' Chapter '),
            ("title", ':  ', ' - Page 1'),
        ), values=data)[0]

    @staticmethod
    def get_images(page):
        return [
            (img["page_image"], None)
            for img in json.loads(
                text.extract(page, "var pages = ", ";")[0]
            )
        ]


class FallenangelsMangaExtractor(MangaExtractor):
    """Extractor for manga from fascans.com"""
    category = "fallenangels"
    pattern = [r"(?:https?://)?((manga|truyen)\.fascans\.com/manga/[^/]+)/?$"]
    scheme = "https"
    test = [
        ("http://manga.fascans.com/manga/trinity-seven", {
            "url": "92699a250ff7d5adcf4b06e6a45b0c05f3426643",
            "keyword": "afc785c37da7c48e639d3a596e8e0401482b628f",
        }),
        ("https://truyen.fascans.com/manga/rakudai-kishi-no-eiyuutan", {
            "url": "51a731a6b82d5eb7a335fbae6b02d06aeb2ab07b",
            "keyword": "2d2a2a5d9ea5925eb9a47bb13d848967f3af086c",
        }),
    ]

    def __init__(self, match):
        MangaExtractor.__init__(self, match)
        self.lang = "vi" if match.group(2) == "truyen" else "en"

    def chapters(self, page):
        language = util.code_to_language(self.lang)
        results = []
        pos = 0
        while True:
            test, pos = text.extract(page, '<li style="', '', pos)
            if test is None:
                return results
            volume , pos = text.extract(page, 'class="volume-', '"', pos)
            url    , pos = text.extract(page, 'href="', '"', pos)
            chapter, pos = text.extract(page, '>', '<', pos)
            title  , pos = text.extract(page, '<em>', '</em>', pos)

            manga, _, chapter = chapter.rpartition(" ")
            chapter, dot, minor = chapter.partition(".")
            results.append((url, {
                "manga": manga,
                "title": text.unescape(title),
                "volume": text.parse_int(volume),
                "chapter": text.parse_int(chapter),
                "chapter_minor": dot + minor,
                "lang": self.lang,
                "language": language,
            }))
