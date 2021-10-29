# -*- coding: utf-8 -*-

# Copyright 2020-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .common import Extractor, Message
from .. import text


class RedgifsExtractor(Extractor):
    """Base class for redgifs extractors"""
    category = "redgifs"
    filename_fmt = "{category}_{gifName}.{extension}"
    archive_fmt = "{gifName}"
    root = "https://www.redgifs.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1).lower()

        formats = self.config("format")
        if formats is None:
            formats = ("mp4", "mobile", "gif")
        elif isinstance(formats, str):
            formats = (formats, "mp4", "mobile", "gif")
        self.formats = formats

    def items(self):
        metadata = self.metadata()
        for gif in self.gifs():
            url = self._process(gif)
            if not url:
                self.log.warning("Skipping '%s' (format not available)",
                                 gif["id"])
                continue

            gif.update(metadata)
            yield Message.Directory, gif
            yield Message.Url, url, gif

    def _process(self, gif):
        gif["_fallback"] = formats = self._formats(gif)
        gif["date"] = text.parse_timestamp(gif.get("createDate"))
        return next(formats, None)

    def _formats(self, gif):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gif:
                url = gif[key]
                if url.startswith("http:"):
                    url = "https" + url[4:]
                text.nameext_from_url(url, gif)
                yield url

    def metadata(self):
        return {}

    def gifs(self):
        return ()


class RedgifsUserExtractor(RedgifsExtractor):
    """Extractor for redgifs user profiles"""
    subcategory = "user"
    directory_fmt = ("{category}", "{userName}")
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/users/([^/?#]+)"
    test = ("https://www.redgifs.com/users/Natalifiction", {
        "pattern": r"https://\w+\.redgifs\.com/[A-Za-z]+\.mp4",
        "count": ">= 120",
    })

    def metadata(self):
        return {"userName": self.key}

    def gifs(self):
        return RedgifsAPI(self).user(self.key)


class RedgifsSearchExtractor(RedgifsExtractor):
    """Extractor for redgifs search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/gifs/browse/([^/?#]+)"
    test = ("https://www.redgifs.com/gifs/browse/jav", {
        "pattern": r"https://\w+\.redgifs\.com/[A-Za-z]+\.mp4",
        "range": "1-10",
        "count": 10,
    })

    def metadata(self):
        self.key = text.unquote(self.key).replace("-", " ")
        return {"search": self.key}

    def gifs(self):
        return RedgifsAPI(self).search(self.key)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:www\.)?(?:redgifs\.com/(?:watch|ifr)"
               r"|gifdeliverynetwork.com)/([A-Za-z]+)")
    test = (
        ("https://redgifs.com/watch/foolishforkedabyssiniancat", {
            "pattern": r"https://\w+\.redgifs\.com"
                       r"/FoolishForkedAbyssiniancat\.mp4",
            "content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
        }),
        ("https://redgifs.com/ifr/FoolishForkedAbyssiniancat"),
        ("https://www.gifdeliverynetwork.com/foolishforkedabyssiniancat"),
    )

    def gifs(self):
        return (RedgifsAPI(self).gif(self.key),)


class RedgifsAPI():
    API_ROOT = "https://api.redgifs.com"

    def __init__(self, extractor):
        self.extractor = extractor

    def gif(self, gif_id):
        endpoint = "/v1/gifs/" + gif_id
        return self._call(endpoint)["gfyItem"]

    def user(self, user):
        endpoint = "/v1/users/{}/gifs".format(user.lower())
        params = {"count": 100}
        return self._pagination(endpoint, params)

    def search(self, query, order="trending"):
        endpoint = "/v1/gifs/search"
        params = {"search_text": query, "count": 150,
                  "order": order, "type": "g"}
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        return self.extractor.request(url, params=params).json()

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            yield from data["gifs"]

            if not data["cursor"]:
                return
            params["cursor"] = data["cursor"]
