# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaiera.com/"""

from . import imhentai

BASE_PATTERN = r"(?:https?://)?(?:www\.)?hentaiera\.com"


class HentaieraExtractor():
    category = "hentaiera"
    root = "https://hentaiera.com"


class HentaieraGalleryExtractor(
        HentaieraExtractor, imhentai.ImhentaiGalleryExtractor):
    """Extractor for hentaiera galleries"""
    pattern = BASE_PATTERN + r"/(?:gallery|view)/(\d+)"
    example = "https://hentaiera.com/gallery/12345/"


class HentaieraTagExtractor(
        HentaieraExtractor, imhentai.ImhentaiTagExtractor):
    """Extractor for hentaiera tag searches"""
    subcategory = "tag"
    pattern = (BASE_PATTERN + r"(/(?:"
               r"artist|category|character|group|language|parody|tag"
               r")/([^/?#]+))")
    example = "https://hentaiera.com/tag/TAG/"


class HentaieraSearchExtractor(
        HentaieraExtractor, imhentai.ImhentaiSearchExtractor):
    """Extractor for hentaiera search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?([^#]+)"
    example = "https://hentaiera.com/search/?key=QUERY"


HentaieraExtractor._gallery_extractor = HentaieraGalleryExtractor
