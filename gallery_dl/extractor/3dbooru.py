# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for http://behoimi.org/"""

from . import moebooru


class _3dbooruBase():
    """Base class for 3dbooru extractors"""
    category = "3dbooru"
    basecategory = "booru"
    root = "http://behoimi.org"

    def _init(self):
        headers = self.session.headers
        headers["Referer"] = "http://behoimi.org/post/show/"
        headers["Accept-Encoding"] = "identity"


class _3dbooruTagExtractor(_3dbooruBase, moebooru.MoebooruTagExtractor):
    """Extractor for images from behoimi.org based on search-tags"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org/post"
               r"(?:/(?:index)?)?\?tags=(?P<tags>[^&#]+)")
    example = "http://behoimi.org/post?tags=TAG"

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPoolExtractor(_3dbooruBase, moebooru.MoebooruPoolExtractor):
    """Extractor for image-pools from behoimi.org"""
    pattern = r"(?:https?://)?(?:www\.)?behoimi\.org/pool/show/(?P<pool>\d+)"
    example = "http://behoimi.org/pool/show/12345"

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPostExtractor(_3dbooruBase, moebooru.MoebooruPostExtractor):
    """Extractor for single images from behoimi.org"""
    pattern = r"(?:https?://)?(?:www\.)?behoimi\.org/post/show/(?P<post>\d+)"
    example = "http://behoimi.org/post/show/12345"

    def posts(self):
        params = {"tags": "id:" + self.post_id}
        return self._pagination(self.root + "/post/index.json", params)


class _3dbooruPopularExtractor(
        _3dbooruBase, moebooru.MoebooruPopularExtractor):
    """Extractor for popular images from behoimi.org"""
    pattern = (r"(?:https?://)?(?:www\.)?behoimi\.org"
               r"/post/popular_(?P<scale>by_(?:day|week|month)|recent)"
               r"(?:\?(?P<query>[^#]*))?")
    example = "http://behoimi.org/post/popular_by_month"
