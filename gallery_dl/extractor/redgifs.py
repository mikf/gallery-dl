# -*- coding: utf-8 -*-

# Copyright 2020-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .common import Extractor, Message
from .. import text
from ..cache import memcache


class RedgifsExtractor(Extractor):
    """Base class for redgifs extractors"""
    category = "redgifs"
    filename_fmt = "{category}_{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.redgifs.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)
        self.api = RedgifsAPI(self)

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
    pattern = r"(?:https?://)?(?:\w+\.)?redgifs\.com/users/([^/?#]+)/?$"
    test = (
        ("https://www.redgifs.com/users/Natalifiction", {
            "pattern": r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
            "count": ">= 100",
        }),
        ("https://v3.redgifs.com/users/lamsinka89", {
            "pattern": r"https://\w+\.redgifs\.com/[\w-]+\.(mp4|jpg)",
            "count": ">= 100",
        }),
    )

    def metadata(self):
        return {"userName": self.key}

    def gifs(self):
        return self.api.user(self.key)


class RedgifsCollectionExtractor(RedgifsExtractor):
    """Extractor for an individual user collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{userName}", "{folderName}")
    archive_fmt = "{folderId}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/([^/?#]+)")
    test = (
        ("https://www.redgifs.com/users/boombah123/collections/2631326bbd", {
            "pattern": r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
            "range": "1-20",
            "count": 20,
        }),
        ("https://www.redgifs.com/users/boombah123/collections/9e6f7dd41f", {
            "pattern": r"https://\w+\.redgifs\.com/[\w-]+\.mp4",
            "range": "1-20",
            "count": 20,
        }),
    )

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.collection_id = match.group(2)

    def metadata(self):
        data = {"userName": self.key}
        data.update(self.api.collection_info(self.key, self.collection_id))
        return data

    def gifs(self):
        return self.api.collection(self.key, self.collection_id)


class RedgifsCollectionsExtractor(RedgifsExtractor):
    """Extractor for redgifs user collections"""
    subcategory = "collections"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/?$")
    test = ("https://www.redgifs.com/users/boombah123/collections", {
        "pattern": (r"https://www\.redgifs\.com/users"
                    r"/boombah123/collections/\w+"),
        "count": ">= 3",
    })

    def items(self):
        for collection in self.api.collections(self.key):
            url = "{}/users/{}/collections/{}".format(
                self.root, self.key, collection["folderId"])
            collection["_extractor"] = RedgifsCollectionExtractor
            yield Message.Queue, url, collection


class RedgifsSearchExtractor(RedgifsExtractor):
    """Extractor for redgifs search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = r"(?:https?://)?(?:\w+\.)?redgifs\.com/browse/?\?([^#]+)"
    test = (
        ("https://www.redgifs.com/browse?tags=JAV", {
            "pattern": r"https://\w+\.redgifs\.com/[A-Za-z-]+\.(mp4|jpg)",
            "range": "1-10",
            "count": 10,
        }),
        ("https://v3.redgifs.com/browse?tags=JAV"),
        ("https://www.redgifs.com/browse?type=i&verified=y&order=top7"),
    )

    def metadata(self):
        self.params = params = text.parse_query(self.key)
        search = params.get("tags") or params.get("order") or "trending"
        return {"search": search}

    def gifs(self):
        return self.api.search(self.params)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?redgifs\.com/(?:watch|ifr)|"
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
        ("https://v3.redgifs.com/watch/FoolishForkedAbyssiniancat"),
    )

    def gifs(self):
        return (self.api.gif(self.key),)


class RedgifsAPI():
    """https://api.redgifs.com/docs/index.html"""

    API_ROOT = "https://api.redgifs.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Referer"       : extractor.root + "/",
            "authorization" : None,
            "content-type"  : "application/json",
            "x-customheader": extractor.root + "/",
            "Origin"        : extractor.root,
        }

    def gif(self, gif_id):
        endpoint = "/v2/gifs/" + gif_id.lower()
        return self._call(endpoint)["gif"]

    def user(self, user, order="best"):
        endpoint = "/v2/users/{}/search".format(user.lower())
        params = {"order": order}
        return self._pagination(endpoint, params)

    def collection(self, user, collection_id):
        endpoint = "/v2/users/{}/collections/{}/gifs".format(
            user, collection_id)
        return self._pagination(endpoint)

    def collection_info(self, user, collection_id):
        endpoint = "/v2/users/{}/collections/{}".format(user, collection_id)
        return self._call(endpoint)

    def collections(self, user):
        endpoint = "/v2/users/{}/collections".format(user)
        return self._pagination(endpoint, key="collections")

    def search(self, params):
        endpoint = "/v2/gifs/search"
        params["search_text"] = params.pop("tags", None)
        params.pop("needSendGtm", None)
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        self.headers["authorization"] = self._auth()
        return self.extractor.request(
            url, params=params, headers=self.headers).json()

    def _pagination(self, endpoint, params=None, key="gifs"):
        if params is None:
            params = {}
        params["page"] = 1

        while True:
            data = self._call(endpoint, params)
            yield from data[key]

            if params["page"] >= data["pages"]:
                return
            params["page"] += 1

    @memcache(maxage=600)
    def _auth(self):
        # https://github.com/Redgifs/api/wiki/Temporary-tokens
        url = self.API_ROOT + "/v2/auth/temporary"
        self.headers["authorization"] = None
        return "Bearer " + self.extractor.request(
            url, headers=self.headers).json()["token"]
