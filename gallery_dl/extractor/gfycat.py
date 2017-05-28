# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gfycat.com/"""

from .common import Extractor, Message
from .. import exception
from ..cache import cache


class GfycatExtractor(Extractor):
    """Base class for gfycat extractors"""
    category = "gfycat"

    def __init__(self, match):
        Extractor.__init__(self)
        self.api = GfycatAPI(self)
        self.item_id = match.group(1)

    @staticmethod
    def _clean(image):
        for key in ("dislikes", "likes", "views"):
            del image[key]
        return image


class GfycatImageExtractor(GfycatExtractor):
    """Extractor for individual images from gfycat.com"""
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{gfyName}.{extension}"
    pattern = [r"(?:https?://)?(?:[a-z]+\.)?gfycat\.com/"
               r"(?:detail/)?((?:[A-Z][a-z]+)+)"]
    test = [
        ("https://gfycat.com/GrayGenerousCowrie", {
            "url": "6a9eca1d7f4d9a2c590c92ec723fd63dc12140c6",
            "keyword": "5887d4582c0b848440e4d21f0ff941927df18fa9",
            "content": "4c2ccc216ac579271d136ed58453be75e776ddad",
        }),
        (("https://thumbs.gfycat.com/SillyLameIsabellinewheatear"
          "-size_restricted.gif"), {
            "url": "96d61307fcf95e6d8e08bea66fd36a1a20b342f0",
        }),
        ("https://gfycat.com/detail/UnequaledHastyAnkole?tagname=aww", {
            "url": "1063429f09463128ce93cfbd885229a4e9f1b383",
        }),
    ]

    def items(self):
        image = self._clean(self.api.gfycats(self.item_id))
        yield Message.Version, 1
        yield Message.Directory, image
        # TODO: support other formats (gif, mp4)
        yield Message.Url, image["webmUrl"], image


class GfycatAPI():
    """Minimal interface for the gfycat API"""
    def __init__(self, extractor):
        self.session = extractor.session

    def gfycats(self, gfycat_id):
        """Return information about a gfycat object"""
        return self._call("gfycats/" + gfycat_id)["gfyItem"]

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        token = self._authenticate_impl()
        self.session.headers["Authorization"] = token

    @cache(maxage=3600)
    def _authenticate_impl(self):
        """Actual authenticate implementation"""
        url = "https://api.gfycat.com/v1/oauth/token"
        data = {"grant_type": "client_credentials",
                "client_id": "2_TFs1Nh",
                "client_secret": ("IZ6qLQ0t7LzxY9P8Rm8Ao4S0sm91o-"
                                  "o2yVkyO4QgDQK2QbVQNMuXks-M3fuwcs3r")}
        response = self.session.post(url, json=data)
        if response.status_code != 200:
            raise exception.AuthenticationError()
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint):
        self.authenticate()
        response = self.session.get("https://api.gfycat.com/v1/" + endpoint)
        if response.status_code == 404:
            raise exception.NotFoundError()
        return response.json()
