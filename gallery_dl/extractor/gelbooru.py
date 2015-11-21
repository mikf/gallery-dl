# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://gelbooru.com/"""

from . import booru
from .. import config

class GelbooruExtractor(booru.XMLBooruExtractor):
    """Base class for gelbooru extractors"""

    category = "gelbooru"
    api_url = "http://gelbooru.com/"

    def setup(self):
        self.params.update({"page":"dapi", "s":"post", "q":"index"})
        self.session.cookies.update(
            config.get(("extractor", self.category, "cookies"))
        )

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"] = 0

class GelbooruTagExtractor(GelbooruExtractor, booru.BooruTagExtractor):
    """Extract images from gelbooru based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?\?page=post&s=list&tags=([^&]+)"]

# TODO: find out how to access pools via gelbooru-api
# class GelbooruPoolExtractor(GelbooruExtractor, booru.BooruPoolExtractor):
    # """Extract image-pools from gelbooru"""
    # pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?\?page=pool&s=show&id=(\d+)"]

class GelbooruPostExtractor(GelbooruExtractor, booru.BooruPostExtractor):
    """Extract single images from gelbooru"""
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?\?page=post&s=view&id=(\d+)"]
