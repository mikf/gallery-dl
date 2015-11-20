# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://danbooru.donmai.us/"""

from . import booru

class DanbooruExtractor(booru.JSONBooruExtractor):
    """Base class for danbooru extractors"""
    category = "danbooru"
    api_url = "https://danbooru.donmai.us/posts.json"

class DanbooruTagExtractor(DanbooruExtractor, booru.BooruTagExtractor):
    """Extract images from danbooru based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts\?(?:utf8=%E2%9C%93&)?tags=([^&]+)"]

class DanbooruPoolExtractor(DanbooruExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from danbooru"""
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/pools/(\d+)"]

class DanbooruPostExtractor(DanbooruExtractor, booru.BooruPostExtractor):
    """Extract single images from danbooru"""
    pattern = [r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts/(\d+)"]
