# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://e621.net/"""

from . import booru

class E621Extractor(booru.JSONBooruExtractor):
    """Base class for e621 extractors"""
    category = "e621"
    api_url = "https://e621.net/post/index.json"

class E621TagExtractor(E621Extractor, booru.BooruTagExtractor):
    """Extract images from e621 based on search-tags"""
    pattern = [
        r"(?:https?://)?(?:www\.)?e621\.net/post/index/\d+/([^?]+)",
        r"(?:https?://)?(?:www\.)?e621\.net/post\?tags=([^&]+)",
    ]

class E621PoolExtractor(E621Extractor, booru.BooruPoolExtractor):
    """Extract image-pools from e621"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/pool/show/(\d+)"]

class E621PostExtractor(E621Extractor, booru.BooruPostExtractor):
    """Extract single images from e621"""
    pattern = [r"(?:https?://)?(?:www\.)?e621\.net/post/show/(\d+)"]
