# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://raw.senmanga.com/"""

from .common import ChapterExtractor
from .. import text


class SenmangaChapterExtractor(ChapterExtractor):
    """Extractor for manga chapters from raw.senmanga.com"""
    category = "senmanga"
    root = "https://raw.senmanga.com"
    pattern = r"(?:https?://)?raw\.senmanga\.com(/[^/?#]+/[^/?#]+)"
    example = "https://raw.senmanga.com/MANGA/CHAPTER"

    def _init(self):
        self.session.headers["Referer"] = self.gallery_url

        # select "All pages" viewer
        self.cookies.set("viewer", "1", domain="raw.senmanga.com")

    def metadata(self, page):
        title = text.extr(page, "<title>", "</title>")
        manga, _, chapter = title.partition(" - Chapter ")

        return {
            "manga"        : text.unescape(manga).replace("-", " "),
            "chapter"      : chapter.partition(" - Page ")[0],
            "chapter_minor": "",
            "lang"         : "ja",
            "language"     : "Japanese",
        }

    def images(self, page):
        return [
            (text.ensure_http_scheme(url), None)
            for url in text.extract_iter(
                page, '<img class="picture" src="', '"')
        ]
