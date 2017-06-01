# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.flickr.com/"""

from .common import Extractor, Message
from .. import text, util, exception


class FlickrExtractor(Extractor):
    """Base class for flickr extractors"""
    category = "flickr"
    filename_fmt = "{category}_{id}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.api = FlickrAPI(self)
        self.item_id = match.group(1)


class FlickrImageExtractor(FlickrExtractor):
    """Extractor for individual images from flickr.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.|m\.)?flickr\.com/photos/[^/]+/(\d+)",
               r"(?:https?://)?[^.]+\.static\.?flickr\.com/(?:\d+/)+(\d+)_",
               r"(?:https?://)?flic\.kr/(p)/([A-Za-z1-9]+)"]
    test = [
        ("https://www.flickr.com/photos/departingyyz/16089302239", {
            "url": "7f0887f5953f61c8b79a695cb102ea309c0346b0",
            "keyword": "5ecdaf0192802451b7daca9b81f393f207ff7ee9",
            "content": "6aaad7512d335ca93286fe2046e7fe3bb93d808e",
        }),
        ("http://c2.staticflickr.com/2/1475/24531000464_9a7503ae68_b.jpg", {
            "url": "40f5163488522ca5d918750ed7bd7fcf437982fe"}),
        ("https://farm2.static.flickr.com/1035/1188352415_cb139831d0.jpg", {
            "url": "ef217b4fdcb148a0cc9eae44b9342d4a65f6d697"}),
        ("https://flic.kr/p/FPVo9U", {
            "url": "92c54a00f31040c349cb2abcb1b9abe30cc508ae"}),
        ("https://www.flickr.com/photos/zzz/16089302238", {
            "exception": exception.NotFoundError}),
    ]

    def __init__(self, match):
        FlickrExtractor.__init__(self, match)
        if self.item_id == "p":
            alphabet = ("123456789abcdefghijkmnopqrstu"
                        "vwxyzABCDEFGHJKLMNPQRSTUVWXYZ")
            self.item_id = util.bdecode(match.group(2), alphabet)
        self.metadata = self.config("metadata", False)

    def items(self):
        size = self.api.photos_getSizes(self.item_id)[-1]

        if self.metadata:
            info = self.api.photos_getInfo(self.item_id)
            self._clean(info)
        else:
            info = {"id": self.item_id}

        info["photo"] = size
        url = size["source"]
        text.nameext_from_url(url, info)

        yield Message.Version, 1
        yield Message.Directory, info
        yield Message.Url, url, info

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


class FlickrAlbumExtractor(FlickrExtractor):
    """Extractor for photo albums from flickr.com"""
    subcategory = "album"
    directory_fmt = ["{category}", "{id} - {title}"]
    pattern = [r"(?:https?://)?(?:www\.)?flickr\.com/"
               r"photos/[^/]+/(?:album|set)s/(\d+)"]
    test = [("https://www.flickr.com/photos/flickr/albums/72157656845052880", {
        "url": "517db3faa55e88686f1d00a379f8f0daf4c7b837",
        "keyword": "504ca926fe520dc6e4a98e7ee590c3498a3c3392",
    })]

    def items(self):
        first = True
        yield Message.Version, 1

        for photo in self.api.photosets_getPhotos(self.item_id):
            if first:
                first = False
                yield Message.Directory, photo["photoset"].copy()
            url = photo["photo"]["source"]
            yield Message.Url, url, text.nameext_from_url(url, photo)


class FlickrAPI():
    """Minimal interface for the flickr API"""
    api_url = "https://api.flickr.com/services/rest/"
    formats = [("o", "Original"), ("k", "Large 2048"),
               ("h", "Large 1600"), ("l", "Large")]

    def __init__(self, extractor, api_key="ac4fd7aa98585b9eee1ba761c209de68"):
        self.session = extractor.session
        self.subcategory = extractor.subcategory
        self.api_key = api_key

    def photos_getInfo(self, photo_id):
        params = {"photo_id": photo_id}
        return self._call("photos.getInfo", params)["photo"]

    def photos_getSizes(self, photo_id):
        params = {"photo_id": photo_id}
        return self._call("photos.getSizes", params)["sizes"]["size"]

    def photosets_getPhotos(self, photoset_id):
        method = "photosets.getPhotos"
        params = {"photoset_id": photoset_id, "page": 1,
                  "extras": "url_o,url_k,url_h,url_l"}
        while True:
            photoset = self._call(method, params)["photoset"]

            photos = photoset["photo"]
            del photoset["photo"]
            del photoset["page"]
            del photoset["perpage"]
            del photoset["per_page"]

            for photo in photos:

                for fmt, fmtname in self.formats:
                    key = "url_" + fmt
                    if key in photo:
                        # generate photo info
                        photo["photo"] = {
                            "source": photo[key],
                            "width" : photo["width_" + fmt],
                            "height": photo["height_" + fmt],
                            "label" : fmtname,
                            "media" : "photo",
                        }
                        # remove excess data
                        keys = [
                            key for key in photo.keys()
                            if key.startswith(("url_", "width_", "height_"))
                        ]
                        for key in keys:
                            del photo[key]
                        break

                else:
                    # extra API call to get photo url and size
                    print(photo["id"])
                    photo["photo"] = self.photos_getSizes(photo["id"])[-1]

                photo["photoset"] = photoset
                yield photo

            if params["page"] == photoset["pages"]:
                break
            params["page"] += 1

    def _call(self, method, params):
        params["method"] = "flickr." + method
        params["api_key"] = self.api_key
        params["format"] = "json"
        params["nojsoncallback"] = "1"
        data = self.session.get(self.api_url, params=params).json()
        if "code" in data and data["code"] == 1:
            raise exception.NotFoundError(self.subcategory)
        return data
