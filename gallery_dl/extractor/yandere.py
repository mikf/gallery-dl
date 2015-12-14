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
    test = [("https://yande.re/post?tags=yuuki_itsuka", {
        "url": "a6df238d4657736eaae9840a0b6a68fb290aa6d5",
        "keyword": "7699bf0fd1dad622c8806f6193fb79f12d40c138",
    })]

class YanderePoolExtractor(YandereExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from yandere"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?yande.re/pool/show/(\d+)"]
    test = [("https://yande.re/pool/show/12", {
        "url": "07f32d2b70c3dc6b014597a49b9fa4e8c274989f",
        "keyword": "963e9dacc8f4dd5f0bc46f2f187e94b71e35d950",
    })]

class YanderePostExtractor(YandereExtractor, booru.BooruPostExtractor):
    """Extract single images from yandere"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?yande.re/post/show/(\d+)"]
    test = [("https://yande.re/post/show/298952", {
        "url": "ce0c3c29ee968b45db4e4ed5ad3fe8e7ecfb2e33",
        "keyword": "ddc1f3c071f4e87e80394982d35f384a12119ca6",
    })]
