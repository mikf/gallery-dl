# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
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
    filename_fmt = \
        "{category}_{gallery:?//[:11]}{num:?_/_/>02}{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.redgifs.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)

    def _init(self):
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

            gallery = gif.get("gallery")
            if gallery:
                gifs = self.api.gallery(gallery)["gifs"]
                enum = 1
                cnt = len(gifs)
            else:
                gifs = (gif,)
                enum = 0
                cnt = 1

            gif.update(metadata)
            gif["count"] = cnt
            gif["date"] = text.parse_timestamp(gif.get("createDate"))
            yield Message.Directory, gif

            for num, gif in enumerate(gifs, enum):
                gif["_fallback"] = formats = self._formats(gif)
                url = next(formats, None)

                if not url:
                    self.log.warning(
                        "Skipping '%s' (format not available)", gif["id"])
                    continue

                gif["num"] = num
                gif["count"] = cnt
                yield Message.Url, url, gif

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
    pattern = (r"(?:https?://)?(?:\w+\.)?redgifs\.com/users/([^/?#]+)/?"
               r"(?:\?([^#]+))?$")
    example = "https://www.redgifs.com/users/USER"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.query = match.group(2)

    def metadata(self):
        return {"userName": self.key}

    def gifs(self):
        order = text.parse_query(self.query).get("order")
        return self.api.user(self.key, order or "new")


class RedgifsCollectionExtractor(RedgifsExtractor):
    """Extractor for an individual user collection"""
    subcategory = "collection"
    directory_fmt = (
        "{category}", "{collection[userName]}", "{collection[folderName]}")
    archive_fmt = "{collection[folderId]}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/([^/?#]+)")
    example = "https://www.redgifs.com/users/USER/collections/ID"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.collection_id = match.group(2)

    def metadata(self):
        collection = self.api.collection_info(self.key, self.collection_id)
        collection["userName"] = self.key
        return {"collection": collection}

    def gifs(self):
        return self.api.collection(self.key, self.collection_id)


class RedgifsCollectionsExtractor(RedgifsExtractor):
    """Extractor for redgifs user collections"""
    subcategory = "collections"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/users"
               r"/([^/?#]+)/collections/?$")
    example = "https://www.redgifs.com/users/USER/collections"

    def items(self):
        for collection in self.api.collections(self.key):
            url = "{}/users/{}/collections/{}".format(
                self.root, self.key, collection["folderId"])
            collection["_extractor"] = RedgifsCollectionExtractor
            yield Message.Queue, url, collection


class RedgifsNichesExtractor(RedgifsExtractor):
    """Extractor for redgifs niches"""
    subcategory = "niches"
    pattern = (r"(?:https?://)?(?:www\.)?redgifs\.com/niches/([^/?#]+)/?"
               r"(?:\?([^#]+))?$")
    example = "https://www.redgifs.com/niches/NAME"

    def __init__(self, match):
        RedgifsExtractor.__init__(self, match)
        self.query = match.group(2)

    def gifs(self):
        order = text.parse_query(self.query).get("order")
        return self.api.niches(self.key, order or "new")


class RedgifsSearchExtractor(RedgifsExtractor):
    """Extractor for redgifs search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Search", "{search}")
    pattern = (r"(?:https?://)?(?:\w+\.)?redgifs\.com"
               r"/(?:gifs/([^/?#]+)|search(?:/gifs)?()|browse)"
               r"(?:/?\?([^#]+))?")
    example = "https://www.redgifs.com/gifs/TAG"

    def metadata(self):
        tag, self.search, query = self.groups

        self.params = params = text.parse_query(query)
        if tag is not None:
            params["tags"] = text.unquote(tag)

        return {"search": (params.get("query") or
                           params.get("tags") or
                           params.get("order") or
                           "trending")}

    def gifs(self):
        if self.search is None:
            return self.api.gifs_search(self.params)
        else:
            return self.api.search_gifs(self.params)


class RedgifsImageExtractor(RedgifsExtractor):
    """Extractor for individual gifs from redgifs.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:"
               r"(?:\w+\.)?redgifs\.com/(?:watch|ifr)|"
               r"(?:\w+\.)?gfycat\.com(?:/gifs/detail|/\w+)?|"
               r"(?:www\.)?gifdeliverynetwork\.com|"
               r"i\.redgifs\.com/i)/([A-Za-z0-9]+)")
    example = "https://redgifs.com/watch/ID"

    def gifs(self):
        return (self.api.gif(self.key),)


class RedgifsAPI():
    """https://api.redgifs.com/docs/index.html"""

    API_ROOT = "https://api.redgifs.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Accept"        : "application/json, text/plain, */*",
            "Referer"       : extractor.root + "/",
            "Authorization" : None,
            "Origin"        : extractor.root,
        }

    def gif(self, gif_id):
        endpoint = "/v2/gifs/" + gif_id.lower()
        return self._call(endpoint)["gif"]

    def gallery(self, gallery_id):
        endpoint = "/v2/gallery/" + gallery_id
        return self._call(endpoint)

    def user(self, user, order="new"):
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

    def niches(self, niche, order):
        endpoint = "/v2/niches/{}/gifs".format(niche)
        params = {"count": 30, "order": order}
        return self._pagination(endpoint, params)

    def gifs_search(self, params):
        endpoint = "/v2/gifs/search"
        params["search_text"] = params.pop("tags", None)
        return self._pagination(endpoint, params)

    def search_gifs(self, params):
        endpoint = "/v2/search/gifs"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = self.API_ROOT + endpoint
        self.headers["Authorization"] = self._auth()
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
        self.headers["Authorization"] = None
        return "Bearer " + self.extractor.request(
            url, headers=self.headers).json()["token"]
