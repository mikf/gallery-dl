# -*- coding: utf-8 -*-

# Copyright 2020-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .common import Extractor, Message
from .. import text
from ..cache import cache


class RedgifsExtractor(Extractor):
    """Base class for redgifs extractors"""
    category = "redgifs"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.redgifs.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)

        formats = self.config("format")
        if formats is None:
            formats = ("hd", "sd", "gif")
        elif isinstance(formats, str):
            formats = (formats, "hd", "sd", "gif")
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
        urls = gif["urls"]
        for fmt in self.formats:
            url = urls.get(fmt)
            if url:
                url = url.replace("//thumbs2.", "//thumbs3.", 1)
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
    pattern = r"(?:https?://)?(?:www\.)?redgifs\.com/browse/?\?([^#]+)"
    test = (
        ("https://www.redgifs.com/browse?tags=JAV", {
            "pattern": r"https://\w+\.redgifs\.com/[A-Za-z-]+\.mp4",
            "range": "1-10",
            "count": 10,
        }),
        ("https://www.redgifs.com/browse?type=i&verified=y&order=top7"),
    )

    def metadata(self):
        self.params = params = text.parse_query(self.key)
        search = params.get("tags") or params.get("order") or "trending"
        return {"search": search}

    def gifs(self):
        return RedgifsAPI(self).search(self.params)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:www\.)?redgifs\.com/(?:watch|ifr)|"
               r"(?:www\.)?gifdeliverynetwork\.com|"
               r"i\.redgifs\.com/i)/([A-Za-z]+)")
    test = (
        ("https://redgifs.com/watch/foolishforkedabyssiniancat", {
            "pattern": r"https://\w+\.redgifs\.com"
                       r"/FoolishForkedAbyssiniancat\.mp4",
            "content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
        }),
        ("https://redgifs.com/ifr/FoolishForkedAbyssiniancat"),
        ("https://i.redgifs.com/i/FoolishForkedAbyssiniancat"),
        ("https://www.gifdeliverynetwork.com/foolishforkedabyssiniancat"),
    )

    def gifs(self):
        return (RedgifsAPI(self).gif(self.key),)


class RedgifsAPI():
    API_ROOT = "https://api.redgifs.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Referer"      : extractor.root + "/",
            "authorization": "Bearer " + self._fetch_bearer_token(extractor),
            "content-type" : "application/json",
            "Origin"       : extractor.root,
        }

    def gif(self, gif_id):
        endpoint = "/v2/gifs/" + gif_id.lower()
        return self._call(endpoint)["gif"]

    def user(self, user, order="best"):
        endpoint = "/v2/users/{}/search".format(user.lower())
        params = {"order": order}
        return self._pagination(endpoint, params)

    def search(self, params):
        endpoint = "/v2/gifs/search"
        params["search_text"] = params.pop("tags", None)
        params.pop("needSendGtm", None)
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        return self.extractor.request(
            url, params=params, headers=self.headers).json()

    def _pagination(self, endpoint, params):
        params["page"] = 1

        while True:
            data = self._call(endpoint, params)
            yield from data["gifs"]

            if params["page"] >= data["pages"]:
                return
            params["page"] += 1

    @cache(maxage=3600)
    def _fetch_bearer_token(self, extr):
        extr.log.debug("Retrieving Bearer token")

        page = extr.request(extr.root + "/").text
        index = text.extract(page, "/assets/js/index", ".js")[0]

        url = extr.root + "/assets/js/index" + index + ".js"
        page = extr.request(url, encoding="utf-8").text
        token = "ey" + text.extract(page, '="ey', '"')[0]

        extr.log.debug("Token: '%s'", token)
        return token
