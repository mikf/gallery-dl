# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://behoimi.org/"""

from . import booru

class ThreeDeeBooruExtractor(booru.JSONBooruExtractor):
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    api_url = "http://behoimi.org/post/index.json"
    headers = {
        "Referer": "http://behoimi.org/post/show/",
        "User-Agent": "Mozilla/5.0",
    }

class ThreeDeeBooruTagExtractor(ThreeDeeBooruExtractor, booru.BooruTagExtractor):
    """Extract images from 3dbooru based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post(?:/(?:index)?)?\?tags=([^&]+)"]

class ThreeDeeBooruPoolExtractor(ThreeDeeBooruExtractor, booru.BooruPoolExtractor):
    """Extract image-pools from 3dbooru"""
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(\d+)"]

class ThreeDeeBooruPostExtractor(ThreeDeeBooruExtractor, booru.BooruPostExtractor):
    """Extract single images from 3dbooru"""
    pattern = [r"(?:https?://)?(?:www\.)?behoimi\.org/post/show/(\d+)"]
