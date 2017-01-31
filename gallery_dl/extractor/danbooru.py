# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://danbooru.donmai.us/"""

from . import booru


class DanbooruExtractor(booru.JSONBooruExtractor):
    """Base class for danbooru extractors"""
    category = "danbooru"
    api_url = "https://danbooru.donmai.us/posts.json"


class DanbooruTagExtractor(DanbooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from danbooru based on search-tags"""
    subcategory = "tag"
    pattern = [(r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts"
                r"\?(?:utf8=%E2%9C%93&)?tags=([^&]+)")]
    test = [("https://danbooru.donmai.us/posts?tags=bonocho", {
        "url": "fb730af3f5e15650e5d924ffcda54b9ef232b89b",
        "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
    })]


class DanbooruPoolExtractor(DanbooruExtractor, booru.BooruPoolExtractor):
    """Extractor for image-pools from danbooru"""
    subcategory = "pool"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/pools/(\d+)"]
    test = [("https://danbooru.donmai.us/pools/7659", {
        "url": "73c02ec3d67ffd46d489dd6cfd7b35fee053865c",
        "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
    })]


class DanbooruPostExtractor(DanbooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from danbooru"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts/(\d+)"]
    test = [("https://danbooru.donmai.us/posts/294929", {
        "url": "9caa006a4d9eedbacbe030655ade0d3225399749",
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]
