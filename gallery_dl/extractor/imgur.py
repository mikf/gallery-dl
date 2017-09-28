# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://imgur.com/"""

from .common import Extractor, Message
from .. import text, exception
import json


class ImgurExtractor(Extractor):
    """Base class for imgur extractors"""
    category = "imgur"

    def __init__(self, match):
        Extractor.__init__(self)
        self.item_id = match.group(1)
        self.mp4 = self.config("mp4", True)

    def _get_data(self, urlpart):
        response = self.request("https://imgur.com/" + urlpart, fatal=False)
        if response.status_code == 404:
            raise exception.NotFoundError(self.subcategory)
        data = text.extract(response.text, "image               : ", ",\n")[0]
        return self._clean(json.loads(data))

    def _prepare(self, image):
        if image["ext"] == ".gif" and (
                (self.mp4 and image["prefer_video"]) or self.mp4 == "always"):
            image["ext"] = ".mp4"
        url = "https://i.imgur.com/" + image["hash"] + image["ext"]
        image["extension"] = image["ext"][1:]
        return url

    @staticmethod
    def _clean(data):
        try:
            del data["views"]
            del data["adConfig"]
            del data["isAd"]
            del data["date"]
        except KeyError:
            pass
        return data


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images from imgur.com"""
    subcategory = "image"
    filename_fmt = "{category}_{hash}{title:?_//}.{extension}"
    pattern = [(r"(?:https?://)?(?:m\.|www\.)?imgur\.com/"
                r"(?:gallery/)?((?!gallery)[^/?&#]{7})/?"),
               (r"(?:https?://)?i\.imgur\.com/([^/?&#.]{5,7})\.")]
    test = [
        ("https://imgur.com/21yMxCS", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "keyword": "834b6714d6daf0f8df99f6261e9bb5f3ccbbcfdb",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("https://i.imgur.com/21yMxCS.png", {  # direct link
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "keyword": "834b6714d6daf0f8df99f6261e9bb5f3ccbbcfdb",
        }),
        ("http://imgur.com/0gybAXR", {  # gifv/mp4 video
            "url": "a2220eb265a55b0c95e0d3d721ec7665460e3fd7",
            "keyword": "94c3d9df06db5ffd1840be3b94c100ced19b4751",
            "content": "a3c080e43f58f55243ab830569ba02309d59abfc",
        }),
        ("https://imgur.com/zzzzzzz", {
            "exception": exception.NotFoundError,
        }),
    ]

    def items(self):
        image = self._get_data(self.item_id)
        url = self._prepare(image)

        yield Message.Version, 1
        yield Message.Directory, image
        yield Message.Url, url, image


class ImgurAlbumExtractor(ImgurExtractor):
    """Extractor for image albums from imgur.com"""
    subcategory = "album"
    directory_fmt = ["{category}", "{album[hash]}{album[title]:? - //}"]
    filename_fmt = "{category}_{album[hash]}_{num:>03}_{hash}.{extension}"
    pattern = [r"(?:https?://)?(?:m\.|www\.)?imgur\.com/"
               r"(?:a|gallery)/([^/?&#]{5})/?$"]
    test = [
        ("https://imgur.com/a/TcBmP", {
            "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
            "keyword": "4fb9d3089810ce5d230f2706b3b37edf529061bf",
        }),
        ("https://imgur.com/gallery/eD9CT", {  # large album
            "url": "4ee94de31ff26be416271bc0b1ea27b9349c9937",
            "keyword": "577f15a6320b7717bd9fd04e7fde56f9519e3def",
        }),
        ("https://imgur.com/a/TcBmQ", {
            "exception": exception.NotFoundError,
        }),
    ]

    def items(self):
        album = self._get_data("a/" + self.item_id + "/all")
        images = album["album_images"]["images"]
        del album["album_images"]

        if int(album["num_images"]) > len(images):
            url = ("https://imgur.com/ajaxalbums/getimages/" +
                   self.item_id + "/hit.json")
            images = self.request(url).json()["data"]["images"]

        yield Message.Version, 1
        yield Message.Directory, {"album": album, "count": len(images)}
        for num, image in enumerate(images, 1):
            url = self._prepare(image)
            image["num"] = num
            image["album"] = album
            yield Message.Url, url, image
