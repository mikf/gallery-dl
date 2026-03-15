# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://toonily.com/"""

from .. import text
from .wpmadara import (
    WPMadaraChapterExtractor,
    WPMadaraHomeExtractor,
    WPMadaraMangaExtractor,
)


class ToonilyChapterExtractor(WPMadaraChapterExtractor):
    """Extractor for manga chapters from toonily.com"""
    category = "toonily"
    root = "https://toonily.com"
    cookies_domain = ".toonily.com"
    pattern = r"(?:https?://)?(?:www\.)?toonily\.com(/serie/[^/?#]+/[^/?#]+)"
    example = "https://toonily.com/serie/MANGA/chapter-1/"

    def initialize(self):
        WPMadaraChapterExtractor.initialize(self)
        if not self.config("family-mode", False):
            self.cookies.update({"toonily-mature": "1"})

    def images(self, page):
        return [
            (url, data)
            for url, data in WPMadaraChapterExtractor.images(self, page)
            if "wp-content/assets" not in url
        ]


class ToonilyMangaExtractor(WPMadaraMangaExtractor):
    """Extractor for manga from toonily.com"""
    category = "toonily"
    chapterclass = ToonilyChapterExtractor
    root = "https://toonily.com"
    cookies_domain = ".toonily.com"
    pattern = r"(?:https?://)?(?:www\.)?toonily\.com(/serie/[^/?#]+)/?$"
    example = "https://toonily.com/serie/MANGA/"

    def initialize(self):
        WPMadaraMangaExtractor.initialize(self)
        if not self.config("family-mode", False):
            self.cookies.update({"toonily-mature": "1"})


class ToonilyListExtractor(WPMadaraHomeExtractor):
    """Base class for manga listings from toonily.com"""
    category = "toonily"
    root = "https://toonily.com"
    cookies_domain = ".toonily.com"
    mangaextractor = ToonilyMangaExtractor

    def initialize(self):
        WPMadaraHomeExtractor.initialize(self)
        if not self.config("family-mode", False):
            self.cookies.update({"toonily-mature": "1"})


class ToonilyHomeExtractor(ToonilyListExtractor):
    """Extractor for manga listings from toonily.com"""
    pattern = r"(?:https?://)?(?:www\.)?toonily\.com(?:/page/(\d+))?/?$"
    example = "https://toonily.com/"


class ToonilyTaxonomyExtractor(ToonilyListExtractor):
    """Base class for taxonomy listings from toonily.com"""
    taxonomy = ""

    def __init__(self, match):
        ToonilyListExtractor.__init__(self, match)
        self.term = match[1]
        self.page = text.parse_int(match[2], 1)

    def page_url(self, page_num):
        url = "{}/{}/{}/".format(
            self.root.rstrip("/"), self.taxonomy, self.term)
        if page_num == 1:
            return url
        return "{}page/{}/".format(url, page_num)


class ToonilyTagExtractor(ToonilyTaxonomyExtractor):
    """Extractor for tag listings from toonily.com"""
    subcategory = "tag"
    taxonomy = "tag"
    pattern = (r"(?:https?://)?(?:www\.)?toonily\.com/tag/"
               r"([^/?#]+)(?:/page/(\d+))?/?$")
    example = "https://toonily.com/tag/TAG/"


class ToonilyGenreExtractor(ToonilyTaxonomyExtractor):
    """Extractor for genre listings from toonily.com"""
    subcategory = "genre"
    taxonomy = "genre"
    pattern = (r"(?:https?://)?(?:www\.)?toonily\.com/genre/"
               r"([^/?#]+)(?:/page/(\d+))?/?$")
    example = "https://toonily.com/genre/GENRE/"
