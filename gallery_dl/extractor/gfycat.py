# -*- coding: utf-8 -*-

# Copyright 2017-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://gfycat.com/"""

from .common import Extractor, Message
from .. import text, exception


class GfycatExtractor(Extractor):
    """Base class for gfycat extractors"""
    category = "gfycat"
    filename_fmt = "{category}_{gfyName}{title:?_//}.{extension}"
    archive_fmt = "{gfyName}"
    root = "https://gfycat.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1).lower()

        formats = self.config("format")
        if formats is None:
            formats = ("mp4", "webm", "mobile", "gif")
        elif isinstance(formats, str):
            formats = (formats, "mp4", "webm", "mobile", "gif")
        self.formats = formats

    def items(self):
        metadata = self.metadata()
        for gfycat in self.gfycats():
            if "gfyName" not in gfycat:
                self.log.warning("Skipping '%s' (malformed)", gfycat["gfyId"])
                continue

            url = self._process(gfycat)
            if not url:
                self.log.warning("Skipping '%s' (format not available)",
                                 gfycat["gfyId"])
                continue

            gfycat.update(metadata)
            yield Message.Directory, gfycat
            yield Message.Url, url, gfycat

    def _process(self, gfycat):
        gfycat["_fallback"] = formats = self._formats(gfycat)
        gfycat["date"] = text.parse_timestamp(gfycat.get("createDate"))
        return next(formats, None)

    def _formats(self, gfycat):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gfycat:
                url = gfycat[key]
                if url.startswith("http:"):
                    url = "https" + url[4:]
                gfycat["extension"] = url.rpartition(".")[2]
                yield url

    def metadata(self):
        return {}

    def gfycats(self):
        return ()


class GfycatUserExtractor(GfycatExtractor):
    """Extractor for gfycat user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{username}")
    pattern = r"(?:https?://)?gfycat\.com/@([^/?#]+)/?(?:$|\?|#)"
    test = ("https://gfycat.com/@gretta", {
        "pattern": r"https://giant\.gfycat\.com/[A-Za-z]+\.mp4",
        "count": ">= 100",
    })

    def gfycats(self):
        return GfycatAPI(self).user(self.key)


class GfycatCollectionExtractor(GfycatExtractor):
    """Extractor for a gfycat collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{collection_owner}",
                     "{collection_name|collection_id}")
    pattern = (r"(?:https?://)?gfycat\.com/@([^/?#]+)/collections"
               r"/(\w+)(?:/([^/?#]+))?")
    test = ("https://gfycat.com/@reactions/collections/nHgy2DtE/no-text", {
        "pattern": r"https://\w+\.gfycat\.com/[A-Za-z]+\.mp4",
        "count": ">= 100",
    })

    def __init__(self, match):
        GfycatExtractor.__init__(self, match)
        self.collection_id = match.group(2)
        self.collection_name = match.group(3)

    def metadata(self):
        return {
            "collection_owner": self.key,
            "collection_name" : self.collection_name,
            "collection_id"   : self.collection_id,
        }

    def gfycats(self):
        return GfycatAPI(self).collection(self.key, self.collection_id)


class GfycatCollectionsExtractor(GfycatExtractor):
    """Extractor for a gfycat user's collections"""
    subcategory = "collections"
    pattern = r"(?:https?://)?gfycat\.com/@([^/?#]+)/collections/?(?:$|\?|#)"
    test = ("https://gfycat.com/@sannahparker/collections", {
        "pattern": GfycatCollectionExtractor.pattern,
        "count": ">= 20",
    })

    def items(self):
        for col in GfycatAPI(self).collections(self.key):
            url = "https://gfycat.com/@{}/collections/{}/{}".format(
                col["userId"], col["folderId"], col["linkText"])
            col["_extractor"] = GfycatCollectionExtractor
            yield Message.Queue, url, col


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
                "gfyNumber": 755075459,
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
            url = self._process(gfycat)
            if not url:
                self.log.warning("Skipping '%s' (format not available)",
                                 gfycat["gfyId"])
                return
            yield Message.Directory, gfycat
            yield Message.Url, url, gfycat


class GfycatAPI():
    API_ROOT = "https://api.gfycat.com"

    def __init__(self, extractor):
        self.extractor = extractor

    def gfycat(self, gfycat_id):
        endpoint = "/v1/gfycats/" + gfycat_id
        return self._call(endpoint)["gfyItem"]

    def user(self, user):
        endpoint = "/v1/users/{}/gfycats".format(user.lower())
        params = {"count": 100}
        return self._pagination(endpoint, params)

    def collection(self, user, collection):
        endpoint = "/v1/users/{}/collections/{}/gfycats".format(
            user, collection)
        params = {"count": 100}
        return self._pagination(endpoint, params)

    def collections(self, user):
        endpoint = "/v1/users/{}/collections".format(user)
        params = {"count": 100}
        return self._pagination(endpoint, params, "gfyCollections")

    def search(self, query):
        endpoint = "/v1/gfycats/search"
        params = {"search_text": query, "count": 150}
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        return self.extractor.request(url, params=params).json()

    def _pagination(self, endpoint, params, key="gfycats"):
        while True:
            data = self._call(endpoint, params)
            yield from data[key]

            if not data["cursor"]:
                return
            params["cursor"] = data["cursor"]
