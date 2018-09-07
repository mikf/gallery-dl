# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentai.cafe/"""

from . import foolslide
from .. import text
import re


class HentaicafeChapterExtractor(foolslide.FoolslideChapterExtractor):
    """Extractor for manga-chapters from hentai.cafe"""
    category = "hentaicafe"
    directory_fmt = ["{category}", "{manga}"]
    pattern = foolslide.chapter_pattern(r"(?:www\.)?hentai\.cafe/manga")
    test = [("https://hentai.cafe/manga/read/saitom-box/en/0/1/", {
        "url": "8c6a8c56875ba3ed7ab0a74a64f9960077767fc2",
        "keyword": "1b24a3e8625b89d160d01ce3eb5e5eb12fbbf648",
    })]

    def get_metadata(self, page):
        info = text.unescape(text.extract(page, '<title>', '</title>')[0])
        manga, _, chapter_string = info.partition(" :: ")
        return self.parse_chapter_url(self.url, {
            "manga": manga,
            "chapter_string": chapter_string.rstrip(" :"),
        })


class HentaicafeMangaExtractor(foolslide.FoolslideMangaExtractor):
    """Extractor for manga from hentai.cafe"""
    category = "hentaicafe"
    pattern = [r"(?:https?://)?((?:www\.)?hentai\.cafe"
               r"(?:/manga/series)?/[^/?&#]+/?$)"]
    test = [
        # single chapter
        ("https://hentai.cafe/hazuki-yuuto-summer-blues/", {
            "url": "f8e24a07d6fbb7c6a6ec5ad8ad8faf2436f8751b",
        }),
        # multi-chapter
        ("https://hentai.cafe/saitom-saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
        }),
        # foolslide URL
        ("https://hentai.cafe/manga/series/saitom-box/", {
            "url": "ca3e8a91531fd6acd863d93ac3afbd8ead06a076",
            "keyword": "46012b857eb1a1394bc55c0efe7aa4e7f704d10d",
        }),
    ]
    reverse = False

    def chapters(self, page):
        if "/manga/series/" in self.url:
            chapters = foolslide.FoolslideMangaExtractor.chapters(self, page)
            chapters.reverse()
            return chapters

        return [
            (url, {})
            for url in re.findall(
                r'<a +class="x-btn[^"]*" +href="([^"]+)"', page)
        ]
