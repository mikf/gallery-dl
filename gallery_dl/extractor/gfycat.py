# -*- coding: utf-8 -*-

# Copyright 2017-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gfycat.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache


class GfycatExtractor(Extractor):
    """Base class for gfycat extractors"""
    category = "gfycat"
    filename_fmt = "{category}_{gfyName}{title:?_//}.{extension}"
    archive_fmt = "{gfyName}"
    root = "https://gfycat.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1).lower()
        self.formats = (self.config("format", "mp4"), "mp4", "webm", "gif")

    def items(self):
        metadata = self.metadata()
        for gfycat in self.gfycats():
            if "gfyName" not in gfycat:
                self.log.warning("Skipping '%s' (malformed)", gfycat["gfyId"])
                continue
            url = self._select_format(gfycat)
            gfycat.update(metadata)
            gfycat["date"] = text.parse_timestamp(gfycat.get("createDate"))
            yield Message.Directory, gfycat
            yield Message.Url, url, gfycat

    def _select_format(self, gfyitem):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gfyitem:
                url = gfyitem[key]
                if url.startswith("http:"):
                    url = "https" + url[4:]
                gfyitem["extension"] = url.rpartition(".")[2]
                return url
        gfyitem["extension"] = ""
        return ""

    def metadata(self):
        return {}

    def gfycats(self):
        return ()


class GfycatUserExtractor(GfycatExtractor):
    """Extractor for gfycat user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{username|userName}")
    pattern = r"(?:https?://)?gfycat\.com/@([^/?#]+)"
    test = ("https://gfycat.com/@gretta", {
        "pattern": r"https://giant\.gfycat\.com/[A-Za-z]+\.mp4",
        "count": ">= 100",
    })

    def gfycats(self):
        return GfycatAPI(self).user(self.key)


class GfycatSearchExtractor(GfycatExtractor):
    """Extractor for gfycat search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = r"(?:https?://)?gfycat\.com/gifs/search/([^/?#]+)"
    test = ("https://gfycat.com/gifs/search/funny+animals", {
        "pattern": r"https://\w+\.gfycat\.com/[A-Za-z]+\.mp4",
        "archive": False,
        "range": "100-300",
        "count": "> 200",
    })

    def metadata(self):
        self.key = text.unquote(self.key).replace("+", " ")
        return {"search": self.key}

    def gfycats(self):
        return GfycatAPI(self).search(self.key)


class GfycatImageExtractor(GfycatExtractor):
    """Extractor for individual images from gfycat.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:\w+\.)?gfycat\.com"
               r"/(?:gifs/detail/|\w+/)?([A-Za-z]{8,})")
    test = (
        ("https://gfycat.com/GrayGenerousCowrie", {
            "url": "e0b5e1d7223108249b15c3c7898dd358dbfae045",
            "content": "5786028e04b155baa20b87c5f4f77453cd5edc37",
            "keyword": {
                "gfyId": "graygenerouscowrie",
                "gfyName": "GrayGenerousCowrie",
                "gfyNumber": "755075459",
                "title": "Bottom's up",
                "username": "jackson3oh3",
                "createDate": 1495884169,
                "date": "dt:2017-05-27 11:22:49",
                "md5": "a4796e05b0db9ba9ce5140145cd318aa",
                "width": 400,
                "height": 224,
                "frameRate": 23.0,
                "numFrames": 158.0,
                "views": int,
            },
        }),
        (("https://thumbs.gfycat.com/SillyLameIsabellinewheatear"
          "-size_restricted.gif"), {
            "url": "13b32e6cc169d086577d7dd3fd36ee6cdbc02726",
        }),
        ("https://gfycat.com/detail/UnequaledHastyAnkole?tagname=aww", {
            "url": "e24c9f69897fd223343782425a429c5cab6a768e",
        }),
        # retry 404'ed videos on redgifs (#874)
        ("https://www.gfycat.com/foolishforkedabyssiniancat", {
            "pattern": "https://redgifs.com/watch/foolishforkedabyssiniancat",
        }),
        # malformed API response (#902)
        ("https://gfycat.com/illexcitablehairstreak", {
            "count": 0,
        }),
        ("https://gfycat.com/gifs/detail/UnequaledHastyAnkole"),
        ("https://gfycat.com/ifr/UnequaledHastyAnkole"),
        ("https://gfycat.com/ru/UnequaledHastyAnkole"),
    )

    def items(self):
        try:
            gfycat = GfycatAPI(self).gfycat(self.key)
        except exception.HttpError:
            from .redgifs import RedgifsImageExtractor
            url = "https://redgifs.com/watch/" + self.key
            data = {"_extractor": RedgifsImageExtractor}
            yield Message.Queue, url, data
        else:
            if "gfyName" not in gfycat:
                self.log.warning("Skipping '%s' (malformed)", gfycat["gfyId"])
                return
            url = self._select_format(gfycat)
            gfycat["date"] = text.parse_timestamp(gfycat.get("createDate"))
            yield Message.Directory, gfycat
            yield Message.Url, url, gfycat


class GfycatAPI():
    API_ROOT = "https://api.gfycat.com"
    ACCESS_KEY = "Anr96uuqt9EdamSCwK4txKPjMsf2M95Rfa5FLLhPFucu8H5HTzeutyAa"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {}

    def gfycat(self, gfycat_id):
        endpoint = "/v1/gfycats/" + gfycat_id
        return self._call(endpoint)["gfyItem"]

    def user(self, user):
        endpoint = "/v1/users/{}/gfycats".format(user.lower())
        params = {"count": 100}
        return self._pagination(endpoint, params)

    def search(self, query):
        endpoint = "/v1/gfycats/search"
        params = {"search_text": query, "count": 150}
        return self._pagination(endpoint, params)

    @cache(keyarg=1, maxage=3600)
    def _authenticate_impl(self, category):
        url = "https://weblogin." + category + ".com/oauth/webtoken"
        data = {"access_key": self.ACCESS_KEY}
        headers = {"Referer": self.extractor.root + "/",
                   "Origin" : self.extractor.root}
        response = self.extractor.request(
            url, method="POST", headers=headers, json=data)
        return "Bearer " + response.json()["access_token"]

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        self.headers["Authorization"] = self._authenticate_impl(
            self.extractor.category)
        return self.extractor.request(
            url, params=params, headers=self.headers).json()

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            gfycats = data["gfycats"]

            for gfycat in gfycats:
                if "gfyName" not in gfycat:
                    gfycat.update(self.gfycat(gfycat["gfyId"]))
                yield gfycat

            if "found" not in data and len(gfycats) < params["count"] or \
                    not data["gfycats"]:
                return
            params["cursor"] = data["cursor"]
