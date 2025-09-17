# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hdoujin.org/"""

from . import schalenetwork

BASE_PATTERN = r"(?:https?://)?(?:www\.)?(hdoujin\.(?:org|net))"


class HdoujinBase():
    """Base class for hdoujin extractors"""
    category = "hdoujin"
    root = "https://hdoujin.org"
    root_api = "https://api.hdoujin.org"
    root_auth = "https://auth.hdoujin.org"


class HdoujinGalleryExtractor(
        HdoujinBase, schalenetwork.SchalenetworkGalleryExtractor):
    pattern = rf"{BASE_PATTERN}/(?:g|reader)/(\d+)/(\w+)"
    example = "https://hdoujin.org/g/12345/67890abcdef/"


class HdoujinSearchExtractor(
        HdoujinBase, schalenetwork.SchalenetworkSearchExtractor):
    pattern = rf"{BASE_PATTERN}/(?:tag/([^/?#]+)|browse)?(?:/?\?([^#]*))?$"
    example = "https://hdoujin.org/browse?s=QUERY"


class HdoujinFavoriteExtractor(
        HdoujinBase, schalenetwork.SchalenetworkFavoriteExtractor):
    pattern = rf"{BASE_PATTERN}/favorites(?:\?([^#]*))?"
    example = "https://hdoujin.org/favorites"


HdoujinBase.extr_class = HdoujinGalleryExtractor
