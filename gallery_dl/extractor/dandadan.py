# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://dandadan.net/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?dandadan\.net"


class DandadanBase():
    """Base class for dandadan extractors"""
    category = "dandadan"
    root = "https://dandadan.net"


class DandadanChapterExtractor(DandadanBase, ChapterExtractor):
    """Extractor for dandadan manga chapters"""
    pattern = rf"{BASE_PATTERN}(/manga/dandadan-chapter-([^/?#]+)/?)"
    example = "https://dandadan.net/manga/dandadan-chapter-123/"

    def metadata(self, page):
        chapter, sep, minor = text.extr(
            page, "hapter ", " - ").partition(".")
        return {
            "manga"        : "Dandadan",
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": f"{sep}{minor}",
            "lang"         : "en",
        }

    def images(self, page):
        images = [
            (text.extr(figure, 'src="', '"'), None)
            for figure in text.extract_iter(page, "<figure", "</figure>")
        ]

        if images:
            return images

        return [
            (src, None)
            for src in text.extract_iter(
                page, '<img decoding="async" class="aligncenter" src="', '"')
        ]


class DandadanMangaExtractor(DandadanBase, MangaExtractor):
    """Extractor for dandadan manga"""
    chapterclass = DandadanChapterExtractor
    pattern = rf"{BASE_PATTERN}(/)"
    example = "https://dandadan.net/"

    def chapters(self, page):
        data = {}
        return [
            (text.extr(post, 'href="', '"'), data)
            for post in text.extract_iter(page, '<li id="su-post', "</li>")
        ]
