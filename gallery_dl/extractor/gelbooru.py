# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gelbooru.com/"""

from . import booru


class GelbooruExtractor(booru.XMLBooruExtractor):
    """Base class for gelbooru extractors"""
    category = "gelbooru"
    api_url = "https://gelbooru.com/"
    pagestart = 0
    pagekey = "pid"

    def setup(self):
        self.params.update({"page": "dapi", "s": "post", "q": "index"})


class GelbooruTagExtractor(GelbooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=([^&]+)"]
    test = [("http://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
        "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
    })]


# TODO: find out how to access pools via gelbooru-api
# class GelbooruPoolExtractor(GelbooruExtractor, booru.BooruPoolExtractor):
    # """Extractor for image-pools from gelbooru.com"""
    # pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
    #            r"\?page=pool&s=show&id=(\d+)"]


class GelbooruPostExtractor(GelbooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from gelbooru.com"""
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(\d+)"]
    test = [("http://gelbooru.com/index.php?page=post&s=view&id=313638", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]
