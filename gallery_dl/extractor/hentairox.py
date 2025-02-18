# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentairox.com/"""

from . import imhentai

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hentairox\.com"


class HentairoxExtractor():
    category = "hentairox"
    root = "https://hentairox.com"


class HentairoxGalleryExtractor(
        HentairoxExtractor, imhentai.ImhentaiGalleryExtractor):
    """Extractor for hentairox galleries"""
    pattern = BASE_PATTERN + r"/(?:gallery|view)/(\d+)"
    example = "https://hentairox.com/gallery/12345/"


class HentairoxTagExtractor(
        HentairoxExtractor, imhentai.ImhentaiTagExtractor):
    """Extractor for hentairox tag searches"""
    subcategory = "tag"
    pattern = (BASE_PATTERN + r"(/(?:"
               r"artist|category|character|group|language|parody|tag"
               r")/([^/?#]+))")
    example = "https://hentairox.com/tag/TAG/"


class HentairoxSearchExtractor(
        HentairoxExtractor, imhentai.ImhentaiSearchExtractor):
    """Extractor for hentairox search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?([^#]+)"
    example = "https://hentairox.com/search/?key=QUERY"


HentairoxExtractor._gallery_extractor = HentairoxGalleryExtractor
