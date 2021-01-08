# -*- coding: utf-8 -*-

# Copyright 2020-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .gfycat import GfycatExtractor, GfycatAPI
from .. import text


class RedgifsExtractor(GfycatExtractor):
    """Base class for redgifs extractors"""
    category = "redgifs"
    root = "https://www.redgifs.com"


class RedgifsUserExtractor(RedgifsExtractor):
    """Extractor for redgifs user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{userName}")
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/users/([^/?#]+)"
    test = ("https://www.redgifs.com/users/Natalifiction", {
        "pattern": r"https://\w+\.(redgifs|gfycat)\.com/[A-Za-z]+\.mp4",
        "count": ">= 100",
    })

    def gfycats(self):
        return RedgifsAPI(self).user(self.key)


class RedgifsSearchExtractor(RedgifsExtractor):
    """Extractor for redgifs search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/gifs/browse/([^/?#]+)"
    test = ("https://www.redgifs.com/gifs/browse/jav", {
        "pattern": r"https://\w+\.(redgifs|gfycat)\.com/[A-Za-z]+\.mp4",
        "range": "1-10",
        "count": 10,
    })

    def metadata(self):
        self.key = text.unquote(self.key).replace("-", " ")
        return {"search": self.key}

    def gfycats(self):
        return RedgifsAPI(self).search(self.key)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:www\.)?(?:redgifs\.com/(?:watch|ifr)"
               r"|gifdeliverynetwork.com)/([A-Za-z]+)")
    test = (
        ("https://redgifs.com/watch/foolishforkedabyssiniancat", {
            "pattern": r"https://\w+\.(redgifs|gfycat)\.com"
                       r"/FoolishForkedAbyssiniancat\.mp4",
            "content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
        }),
        ("https://redgifs.com/ifr/FoolishForkedAbyssiniancat"),
        ("https://www.gifdeliverynetwork.com/foolishforkedabyssiniancat"),
    )

    def gfycats(self):
        return (RedgifsAPI(self).gfycat(self.key),)


class RedgifsAPI(GfycatAPI):
    API_ROOT = "https://napi.redgifs.com"
    ACCESS_KEY = ("dBLwVuGn9eq4dtXLs8WSfpjcYFY7bPQe"
                  "AqGPSFgqeW5B9uzj2cMVhF63pTFF4Rg9")
