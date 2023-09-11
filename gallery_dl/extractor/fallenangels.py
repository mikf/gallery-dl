# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.fascans.com/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, util


class FallenangelsChapterExtractor(ChapterExtractor):
    """Extractor for manga chapters from fascans.com"""
    category = "fallenangels"
    pattern = (r"(?:https?://)?(manga|truyen)\.fascans\.com"
               r"/manga/([^/?#]+)/([^/?#]+)")
    example = "https://manga.fascans.com/manga/NAME/CHAPTER/"

    def __init__(self, match):
        self.version, self.manga, self.chapter = match.groups()
        url = "https://{}.fascans.com/manga/{}/{}/1".format(
            self.version, self.manga, self.chapter)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        lang = "vi" if self.version == "truyen" else "en"
        chapter, sep, minor = self.chapter.partition(".")
        return {
            "manga"   : extr('name="description" content="', ' Chapter '),
            "title"   : extr(':  ', ' - Page 1'),
            "chapter" : chapter,
            "chapter_minor": sep + minor,
            "lang"    : lang,
            "language": util.code_to_language(lang),
        }

    @staticmethod
    def images(page):
        return [
            (img["page_image"], None)
            for img in util.json_loads(
                text.extr(page, "var pages = ", ";")
            )
        ]


class FallenangelsMangaExtractor(MangaExtractor):
    """Extractor for manga from fascans.com"""
    chapterclass = FallenangelsChapterExtractor
    category = "fallenangels"
    pattern = r"(?:https?://)?((manga|truyen)\.fascans\.com/manga/[^/]+)/?$"
    example = "https://manga.fascans.com/manga/NAME"

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
