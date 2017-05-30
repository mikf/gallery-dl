# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.flickr.com/"""

from .common import Extractor, Message
from .. import text, exception


class FlickrExtractor(Extractor):
    """Base class for flickr extractors"""
    category = "flickr"

    @staticmethod
    def _clean(photo):
        del photo["comments"]
        del photo["views"]

        photo["title"] = photo["title"]["_content"]
        photo["tags"] = [t["raw"] for t in photo["tags"]["tag"]]

        if "location" in photo:
            location = photo["location"]
            for key, value in location.items():
                if isinstance(value, dict):
                    location[key] = value["_content"]


class FlickrImageExtractor(FlickrExtractor):
    """Extractor for individual images from flickr.com"""
    subcategory = "image"
    filename_fmt = "{category}_{id}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/photos/[^/]+/(\d+)",
               r"(?:https?://)?[^.]+\.staticflickr\.com/d+/\d+/(\d+)"]
    test = [
        ("https://www.flickr.com/photos/departingyyz/16089302239", {
            "url": "7f0887f5953f61c8b79a695cb102ea309c0346b0",
            "keyword": "5ecdaf0192802451b7daca9b81f393f207ff7ee9",
            "content": "6aaad7512d335ca93286fe2046e7fe3bb93d808e",
        }),
        ("https://www.flickr.com/photos/zzz/16089302238", {
            "exception": exception.NotFoundError,
        })
    ]

    def __init__(self, match):
        FlickrExtractor.__init__(self)
        self.api = FlickrAPI(self)
        self.photo_id = match.group(1)
        self.metadata = self.config("metadata", False)

    def items(self):
        size = self.api.photos_getSizes(self.photo_id)["size"][-1]

        if self.metadata:
            info = self.api.photos_getInfo(self.photo_id)
            self._clean(info)
        else:
            info = {"id": self.photo_id}

        info["photo"] = size
        url = size["source"]
        text.nameext_from_url(url, info)

        yield Message.Version, 1
        yield Message.Directory, info
        yield Message.Url, url, info


class FlickrAPI():
    api_url = "https://api.flickr.com/services/rest/"

    def __init__(self, extractor, api_key="ac4fd7aa98585b9eee1ba761c209de68"):
        self.session = extractor.session
        self.subcategory = extractor.subcategory
        self.api_key = api_key

    def photos_getInfo(self, photo_id):
        params = {"photo_id": photo_id}
        return self._call("photos.getInfo", params)["photo"]

    def photos_getSizes(self, photo_id):
        params = {"photo_id": photo_id}
        return self._call("photos.getSizes", params)["sizes"]

    def _call(self, method, params):
        params["method"] = "flickr." + method
        params["api_key"] = self.api_key
        params["format"] = "json"
        params["nojsoncallback"] = "1"
        data = self.session.get(self.api_url, params=params).json()
        if "code" in data and data["code"] == 1:
            raise exception.NotFoundError(self.subcategory)
        return data
