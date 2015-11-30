# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://yande.re/"""

from . import booru

class YandereExtractor(booru.JSONBooruExtractor):
    """Base class for yandere extractors"""
    category = "yandere"
    api_url = "https://yande.re/post.json"

class YandereTagExtractor(YandereExtractor, booru.BooruTagExtractor):
    """Extract images from yandere based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?yande\.re/post\?tags=([^&]+)"]

class YanderePoolExtractor(YandereExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from yandere"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?yande.re/pool/show/(\d+)"]

class YanderePostExtractor(YandereExtractor, booru.BooruPostExtractor):
    """Extract single images from yandere"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?yande.re/post/show/(\d+)"]
