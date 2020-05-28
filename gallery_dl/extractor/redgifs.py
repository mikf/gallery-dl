# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .gfycat import GfycatImageExtractor
from ..cache import cache


class RedgifsImageExtractor(GfycatImageExtractor):
    """Extractor for individual images from redgifs.com"""
    category = "redgifs"
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/watch/([A-Za-z]+)"
    test = ("https://redgifs.com/watch/foolishforkedabyssiniancat", {
        "pattern": "https://giant.gfycat.com/FoolishForkedAbyssiniancat.mp4",
        "content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
    })

    def _get_info(self, gfycat_id):
        api = RedgifsAPI(self)
        return api.gfycat(gfycat_id)


class RedgifsAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {}

    def gfycat(self, gfycat_id):
        endpoint = "v1/gfycats/" + gfycat_id
        return self._call(endpoint)["gfyItem"]

    @cache(maxage=3600)
    def _authenticate_impl(self):
        url = "https://weblogin.redgifs.com/oauth/webtoken"
        headers = {
            "Referer": "https://www.redgifs.com/",
            "Origin" : "https://www.redgifs.com",
        }
        data = {
            "access_key": "dBLwVuGn9eq4dtXLs8WSfpjcYFY7bPQe"
                          "AqGPSFgqeW5B9uzj2cMVhF63pTFF4Rg9",
        }

        response = self.extractor.request(
            url, method="POST", headers=headers, json=data)
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint):
        self.headers["Authorization"] = self._authenticate_impl()
        url = "https://napi.redgifs.com/" + endpoint
        return self.extractor.request(url, headers=self.headers).json()
