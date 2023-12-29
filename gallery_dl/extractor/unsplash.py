# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://unsplash.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?unsplash\.com"


class UnsplashExtractor(Extractor):
    """Base class for unsplash extractors"""
    category = "unsplash"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://unsplash.com"
    page_start = 1
    per_page = 20

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def items(self):
        fmt = self.config("format") or "raw"
        metadata = self.metadata()

        for photo in self.photos():
            util.delete_items(
                photo, ("current_user_collections", "related_collections"))
            url = photo["urls"][fmt]
            text.nameext_from_url(url, photo)

            if metadata:
                photo.update(metadata)
            photo["extension"] = "jpg"
            photo["date"] = text.parse_datetime(photo["created_at"])
            if "tags" in photo:
                photo["tags"] = [t["title"] for t in photo["tags"]]

            yield Message.Directory, photo
            yield Message.Url, url, photo

    @staticmethod
    def metadata():
        return None

    def skip(self, num):
        pages = num // self.per_page
        self.page_start += pages
        return pages * self.per_page

    def _pagination(self, url, params, results=False):
        params["per_page"] = self.per_page
        params["page"] = self.page_start

        while True:
            photos = self.request(url, params=params).json()
            if results:
                photos = photos["results"]
            yield from photos

            if len(photos) < self.per_page:
                return
            params["page"] += 1


class UnsplashImageExtractor(UnsplashExtractor):
    """Extractor for a single unsplash photo"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photos/([^/?#]+)"
    example = "https://unsplash.com/photos/ID"

    def photos(self):
        url = "{}/napi/photos/{}".format(self.root, self.item)
        return (self.request(url).json(),)


class UnsplashUserExtractor(UnsplashExtractor):
    """Extractor for all photos of an unsplash user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/@(\w+)/?$"
    example = "https://unsplash.com/@USER"

    def photos(self):
        url = "{}/napi/users/{}/photos".format(self.root, self.item)
        params = {"order_by": "latest"}
        return self._pagination(url, params)


class UnsplashFavoriteExtractor(UnsplashExtractor):
    """Extractor for all likes of an unsplash user"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/@(\w+)/likes"
    example = "https://unsplash.com/@USER/likes"

    def photos(self):
        url = "{}/napi/users/{}/likes".format(self.root, self.item)
        params = {"order_by": "latest"}
        return self._pagination(url, params)


class UnsplashCollectionExtractor(UnsplashExtractor):
    """Extractor for an unsplash collection"""
    subcategory = "collection"
    pattern = BASE_PATTERN + r"/collections/([^/?#]+)(?:/([^/?#]+))?"
    example = "https://unsplash.com/collections/12345/TITLE"

    def __init__(self, match):
        UnsplashExtractor.__init__(self, match)
        self.title = match.group(2) or ""

    def metadata(self):
        return {"collection_id": self.item, "collection_title": self.title}

    def photos(self):
        url = "{}/napi/collections/{}/photos".format(self.root, self.item)
        params = {"order_by": "latest"}
        return self._pagination(url, params)


class UnsplashSearchExtractor(UnsplashExtractor):
    """Extractor for unsplash search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/s/photos/([^/?#]+)(?:\?([^#]+))?"
    example = "https://unsplash.com/s/photos/QUERY"

    def __init__(self, match):
        UnsplashExtractor.__init__(self, match)
        self.query = match.group(2)

    def photos(self):
        url = self.root + "/napi/search/photos"
        params = {"query": text.unquote(self.item.replace('-', ' '))}
        if self.query:
            params.update(text.parse_query(self.query))
        return self._pagination(url, params, True)
