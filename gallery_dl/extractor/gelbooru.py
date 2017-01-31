# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://gelbooru.com/"""

from . import booru
from .. import config


class GelbooruExtractor(booru.XMLBooruExtractor):
    """Base class for gelbooru extractors"""
    category = "gelbooru"
    api_url = "http://gelbooru.com/"

    def setup(self):
        self.params.update({"page": "dapi", "s": "post", "q": "index"})
        try:
            cookies = config.get(("extractor", self.category, "cookies"))
            self.session.cookies.update({
                key: str(value) for key, value in cookies.items()
            })
        except AttributeError:
            pass

    def update_page(self, reset=False):
        if not reset:
            self.params["pid"] += 1
        else:
            self.params["pid"] = 0


class GelbooruTagExtractor(GelbooruExtractor, booru.BooruTagExtractor):
    """Extractor for images from gelbooru.com based on search-tags"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=list&tags=([^&]+)"]
    test = [("http://gelbooru.com/index.php?page=post&s=list&tags=bonocho", {
        "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
    })]


# TODO: find out how to access pools via gelbooru-api
# class GelbooruPoolExtractor(GelbooruExtractor, booru.BooruPoolExtractor):
    # """Extractor for image-pools from gelbooru.com"""
    # subcategory = "pool"
    # pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
    #            r"\?page=pool&s=show&id=(\d+)"]


class GelbooruPostExtractor(GelbooruExtractor, booru.BooruPostExtractor):
    """Extractor for single images from gelbooru.com"""
    subcategory = "post"
    pattern = [r"(?:https?://)?(?:www\.)?gelbooru\.com/(?:index\.php)?"
               r"\?page=post&s=view&id=(\d+)"]
    test = [("http://gelbooru.com/index.php?page=post&s=view&id=313638", {
        "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
    })]
