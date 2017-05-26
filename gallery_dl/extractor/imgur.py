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

    def _get_data(self, urlpart):
        response = self.session.get("https://imgur.com/" + urlpart)
        if response.status_code == 404:
            raise exception.NotFoundError(self.subcategory)
        data = text.extract(response.text, "image               : ", ",\n")[0]
        return self._clean(json.loads(data))

    @staticmethod
    def _prepare(image):
        url = "https://i.imgur.com/" + image["hash"] + image["ext"]
        image["extension"] = image["ext"][1:]
        return url

    @staticmethod
    def _clean(data):
        try:
            del data["views"]
            del data["adConfig"]
            del data["isAd"]
        except KeyError:
            pass
        return data


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images from imgur.com"""
    category = "imgur"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{hash}.{extension}"
    pattern = [(r"(?:https?://)?(?:m\.|www\.)?imgur\.com/"
                r"(?:gallery/)?((?!gallery)[^/?&#]{7})/?"),
               (r"(?:https?://)?i\.imgur\.com/([^/?&#.]{7})\.")]
    test = [
        ("https://imgur.com/21yMxCS", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "keyword": "2270c7a1365c43012231359d2d74d506be6b1a19",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("https://i.imgur.com/21yMxCS.png", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "keyword": "2270c7a1365c43012231359d2d74d506be6b1a19",
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
    directory_fmt = ["{category}", "{album[hash]} - {album[title]}"]
    filename_fmt = "{category}_{album[hash]}_{num:>03}_{hash}.{extension}"
    pattern = [r"(?:https?://)?(?:m\.|www\.)?imgur\.com/"
               r"(?:a|gallery)/([^/?&#]{5})/?$"]
    test = [
        ("https://imgur.com/a/TcBmP", {
            "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
            "keyword": "e2eaae0e62d3c5d76df9c870140d1ef466bbec59",
        }),
        ("https://imgur.com/a/TcBmQ", {
            "exception": exception.NotFoundError,
        }),
    ]

    def items(self):
        album = self._get_data("a/" + self.item_id)
        images = album["album_images"]["images"]
        del album["album_images"]

        yield Message.Version, 1
        yield Message.Directory, {"album": album, "count": len(images)}
        for num, image in enumerate(images, 1):
            url = self._prepare(image)
            image["num"] = num
            image["album"] = album
            yield Message.Url, url, image
