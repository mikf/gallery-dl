# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.webtoon.xyz/"""

from .wpmadara import (
    WPMadaraChapterExtractor,
    WPMadaraHomeExtractor,
    WPMadaraMangaExtractor,
)


class WebtoonxyzBase():
    """Base class for webtoon.xyz extractors"""
    category = "webtoonxyz"
    root = "https://www.webtoon.xyz"
    cookies_domain = ".webtoon.xyz"
    browser = "firefox"

    def initialize(self):
        super().initialize()
        if not self.config("family-mode", False):
            self.cookies.update({"wpmanga-adault": "1"})


class WebtoonxyzChapterExtractor(WebtoonxyzBase, WPMadaraChapterExtractor):
    """Extractor for webtoon.xyz chapter pages"""
    pattern = (
        r"(?:https?://)?(?:www\.)?webtoon\.xyz"
        r"(/read/[^/?#]+/[^/?#]+)"
    )
    example = "https://www.webtoon.xyz/read/MANGA/chapter-1/"


class WebtoonxyzMangaExtractor(WebtoonxyzBase, WPMadaraMangaExtractor):
    """Extractor for webtoon.xyz manga pages"""
    chapterclass = WebtoonxyzChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?webtoon\.xyz(/read/[^/?#]+)/?$"
    example = "https://www.webtoon.xyz/read/MANGA/"


class WebtoonxyzHomeExtractor(WebtoonxyzBase, WPMadaraHomeExtractor):
    """Extractor for the webtoon.xyz home feed"""
    mangaextractor = WebtoonxyzMangaExtractor
    pattern = r"(?:https?://)?(?:www\.)?webtoon\.xyz(?:/page/(\d+))?/?$"
    example = "https://www.webtoon.xyz/"
