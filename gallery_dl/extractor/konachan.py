# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://konachan.com/"""

from . import booru

class KonachanExtractor(booru.JSONBooruExtractor):
    """Base class for konachan extractors"""
    category = "konachan"
    api_url = "https://konachan.com/post.json"

class KonachanTagExtractor(KonachanExtractor, booru.BooruTagExtractor):
    """Extract images from konachan based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post\?tags=([^&]+)"]

class KonachanPoolExtractor(KonachanExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from konachan"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/pool/show/(\d+)"]

class KonachanPostExtractor(KonachanExtractor, booru.BooruPostExtractor):
    """Extract single images from konachan"""
    pattern = [r"(?:https?://)?(?:www\.)?konachan\.com/post/show/(\d+)"]
