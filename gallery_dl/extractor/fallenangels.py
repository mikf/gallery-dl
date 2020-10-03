# -*- coding: utf-8 -*-

# Copyright 2017-2019 Mike Fährmann
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
    pattern = (r"(?:https?://)?(manga|truyen)\.fascans\.com"
               r"/manga/([^/]+)/(\d+)(\.[^/?&#]+)?")
    test = (
        ("https://manga.fascans.com/manga/chronos-ruler/20/1", {
            "url": "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
            "keyword": "2dfcc50020e32cd207be88e2a8fac0933e36bdfb",
        }),
        ("http://truyen.fascans.com/manga/hungry-marie/8", {
            "url": "1f923d9cb337d5e7bbf4323719881794a951c6ae",
            "keyword": "2bdb7334c0e3eceb9946ffd3132df679b4a94f6a",
        }),
        ("http://manga.fascans.com/manga/rakudai-kishi-no-eiyuutan/19.5", {
            "keyword": "9fcca4c1a90d11f00764f62477ebe10bd408021c",
        }),
    )

    def __init__(self, match):
        self.version, self.manga, self.chapter, self.minor = match.groups()
        url = "https://{}.fascans.com/manga/{}/{}/1".format(
            self.version, self.manga, self.chapter)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        lang = "vi" if self.version == "truyen" else "en"
        return {
            "manga"   : extr('name="description" content="', ' Chapter '),
            "title"   : extr(':  ', ' - Page 1'),
            "chapter" : self.chapter,
            "chapter_minor": self.minor or "",
            "lang"    : lang,
            "language": util.code_to_language(lang),
        }

    @staticmethod
    def images(page):
        return [
            (img["page_image"], None)
            for img in json.loads(
                text.extract(page, "var pages = ", ";")[0]
            )
        ]


class FallenangelsMangaExtractor(MangaExtractor):
    """Extractor for manga from fascans.com"""
    chapterclass = FallenangelsChapterExtractor
    category = "fallenangels"
    pattern = r"(?:https?://)?((manga|truyen)\.fascans\.com/manga/[^/]+)/?$"
    test = (
        ("https://manga.fascans.com/manga/chronos-ruler", {
            "url": "eea07dd50f5bc4903aa09e2cc3e45c7241c9a9c2",
            "keyword": "c414249525d4c74ad83498b3c59a813557e59d7e",
        }),
        ("https://truyen.fascans.com/manga/rakudai-kishi-no-eiyuutan", {
            "url": "51a731a6b82d5eb7a335fbae6b02d06aeb2ab07b",
            "keyword": "2d2a2a5d9ea5925eb9a47bb13d848967f3af086c",
        }),
    )

    def __init__(self, match):
        url = "https://" + match.group(1)
        self.lang = "vi" if match.group(2) == "truyen" else "en"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        extr = text.extract_from(page)
        results = []
        language = util.code_to_language(self.lang)
        while extr('<li style="', '"'):
            vol = extr('class="volume-', '"')
            url = extr('href="', '"')
            cha = extr('>', '<')
            title = extr('<em>', '</em>')

            manga, _, chapter = cha.rpartition(" ")
            chapter, dot, minor = chapter.partition(".")
            results.append((url, {
                "manga"   : manga,
                "title"   : text.unescape(title),
                "volume"  : text.parse_int(vol),
                "chapter" : text.parse_int(chapter),
                "chapter_minor": dot + minor,
                "lang"    : self.lang,
                "language": language,
            }))
        return results
