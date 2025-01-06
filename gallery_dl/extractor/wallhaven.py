# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wallhaven.cc/"""

from .common import Extractor, Message
from .. import text, exception


class WallhavenExtractor(Extractor):
    """Base class for wallhaven extractors"""
    category = "wallhaven"
    root = "https://wallhaven.cc"
    filename_fmt = "{category}_{id}_{resolution}.{extension}"
    archive_fmt = "{id}"
    request_interval = 1.4

    def _init(self):
        self.api = WallhavenAPI(self)

    def items(self):
        metadata = self.metadata()
        for wp in self.wallpapers():
            self._transform(wp)
            wp.update(metadata)
            url = wp["url"]
            yield Message.Directory, wp
            yield Message.Url, url, text.nameext_from_url(url, wp)

    def wallpapers(self):
        """Return relevant 'wallpaper' objects"""

    def metadata(self):
        """Return general metadata"""
        return ()

    @staticmethod
    def _transform(wp):
        wp["url"] = wp.pop("path")
        if "tags" in wp:
            wp["tags"] = [t["name"] for t in wp["tags"]]
        wp["date"] = text.parse_datetime(
            wp.pop("created_at"), "%Y-%m-%d %H:%M:%S")
        wp["width"] = wp.pop("dimension_x")
        wp["height"] = wp.pop("dimension_y")
        wp["wh_category"] = wp["category"]


class WallhavenSearchExtractor(WallhavenExtractor):
    """Extractor for search results on wallhaven.cc"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search[tags]}")
    archive_fmt = "s_{search[q]}_{id}"
    pattern = r"(?:https?://)?wallhaven\.cc/search(?:/?\?([^#]+))?"
    example = "https://wallhaven.cc/search?q=QUERY"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def wallpapers(self):
        return self.api.search(self.params)

    def metadata(self):
        return {"search": self.params}


class WallhavenCollectionExtractor(WallhavenExtractor):
    """Extractor for a collection on wallhaven.cc"""
    subcategory = "collection"
    directory_fmt = ("{category}", "{username}", "{collection_id}")
    pattern = r"(?:https?://)?wallhaven\.cc/user/([^/?#]+)/favorites/(\d+)"
    example = "https://wallhaven.cc/user/USER/favorites/12345"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.username, self.collection_id = match.groups()

    def wallpapers(self):
        return self.api.collection(self.username, self.collection_id)

    def metadata(self):
        return {"username": self.username, "collection_id": self.collection_id}


class WallhavenUserExtractor(WallhavenExtractor):
    """Extractor for a wallhaven user"""
    subcategory = "user"
    pattern = r"(?:https?://)?wallhaven\.cc/user/([^/?#]+)/?$"
    example = "https://wallhaven.cc/user/USER"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.username = match.group(1)

    def initialize(self):
        pass

    def items(self):
        base = "{}/user/{}/".format(self.root, self.username)
        return self._dispatch_extractors((
            (WallhavenUploadsExtractor    , base + "uploads"),
            (WallhavenCollectionsExtractor, base + "favorites"),
        ), ("uploads",))


class WallhavenCollectionsExtractor(WallhavenExtractor):
    """Extractor for all collections of a wallhaven user"""
    subcategory = "collections"
    pattern = r"(?:https?://)?wallhaven\.cc/user/([^/?#]+)/favorites/?$"
    example = "https://wallhaven.cc/user/USER/favorites"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.username = match.group(1)

    def items(self):
        for collection in self.api.collections(self.username):
            collection["_extractor"] = WallhavenCollectionExtractor
            url = "https://wallhaven.cc/user/{}/favorites/{}".format(
                self.username, collection["id"])
            yield Message.Queue, url, collection


class WallhavenUploadsExtractor(WallhavenExtractor):
    """Extractor for all uploads of a wallhaven user"""
    subcategory = "uploads"
    directory_fmt = ("{category}", "{username}")
    archive_fmt = "u_{username}_{id}"
    pattern = r"(?:https?://)?wallhaven\.cc/user/([^/?#]+)/uploads"
    example = "https://wallhaven.cc/user/USER/uploads"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.username = match.group(1)

    def wallpapers(self):
        params = {"q": "@" + self.username}
        return self.api.search(params)

    def metadata(self):
        return {"username": self.username}


class WallhavenImageExtractor(WallhavenExtractor):
    """Extractor for individual wallpaper on wallhaven.cc"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:wallhaven\.cc/w/|whvn\.cc/"
               r"|w\.wallhaven\.cc/[a-z]+/\w\w/wallhaven-)(\w+)")
    example = "https://wallhaven.cc/w/ID"

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.wallpaper_id = match.group(1)

    def wallpapers(self):
        return (self.api.info(self.wallpaper_id),)


class WallhavenAPI():
    """Interface for wallhaven's API

    Ref: https://wallhaven.cc/help/api
    """

    def __init__(self, extractor):
        self.extractor = extractor

        key = extractor.config("api-key")
        if key is None:
            key = "25HYZenXTICjzBZXzFSg98uJtcQVrDs2"
            extractor.log.debug("Using default API Key")
        else:
            extractor.log.debug("Using custom API Key")
        self.headers = {"X-API-Key": key}

    def info(self, wallpaper_id):
        endpoint = "/v1/w/" + wallpaper_id
        return self._call(endpoint)["data"]

    def collection(self, username, collection_id):
        endpoint = "/v1/collections/{}/{}".format(username, collection_id)
        return self._pagination(endpoint)

    def collections(self, username):
        endpoint = "/v1/collections/" + username
        return self._pagination(endpoint, metadata=False)

    def search(self, params):
        endpoint = "/v1/search"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = "https://wallhaven.cc/api" + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                self.extractor.wait(seconds=60)
                continue

            self.extractor.log.debug("Server response: %s", response.text)
            raise exception.StopExtraction(
                "API request failed (%s %s)",
                response.status_code, response.reason)

    def _pagination(self, endpoint, params=None, metadata=None):
        if params is None:
            params_ptr = None
            params = {}
        else:
            params_ptr = params
            params = params.copy()
        if metadata is None:
            metadata = self.extractor.config("metadata")

        while True:
            data = self._call(endpoint, params)

            meta = data.get("meta")
            if params_ptr is not None:
                if meta and "query" in meta:
                    query = meta["query"]
                    if isinstance(query, dict):
                        params_ptr["tags"] = query.get("tag")
                        params_ptr["tag_id"] = query.get("id")
                    else:
                        params_ptr["tags"] = query
                        params_ptr["tag_id"] = 0
                params_ptr = None

            if metadata:
                for wp in data["data"]:
                    yield self.info(str(wp["id"]))
            else:
                yield from data["data"]

            if not meta or meta["current_page"] >= meta["last_page"]:
                return
            params["page"] = meta["current_page"] + 1
