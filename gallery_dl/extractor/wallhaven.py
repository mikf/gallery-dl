# -*- coding: utf-8 -*-

# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wallhaven.cc/"""

from .common import Extractor, Message, Dispatch
from .. import text


class WallhavenExtractor(Extractor):
    """Base class for wallhaven extractors"""
    category = "wallhaven"
    root = "https://wallhaven.cc"
    filename_fmt = "{category}_{id}_{resolution}.{extension}"
    archive_fmt = "{id}"
    request_interval = 1.4

    def _init(self):
        self.api = self.utils().WallhavenAPI(self)

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

    def _transform(self, wp):
        wp["url"] = wp.pop("path")
        if "tags" in wp:
            wp["tags"] = [t["name"] for t in wp["tags"]]
        wp["date"] = self.parse_datetime_iso(wp.pop("created_at"))
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
        self.params = text.parse_query(match[1])

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


class WallhavenUserExtractor(Dispatch, WallhavenExtractor):
    """Extractor for a wallhaven user"""
    pattern = r"(?:https?://)?wallhaven\.cc/user/([^/?#]+)/?$"
    example = "https://wallhaven.cc/user/USER"

    def items(self):
        base = f"{self.root}/user/{self.groups[0]}/"
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
        self.username = match[1]

    def items(self):
        base = f"{self.root}/user/{self.username}/favorites/"
        for collection in self.api.collections(self.username):
            collection["_extractor"] = WallhavenCollectionExtractor
            url = f"{base}{collection['id']}"
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
        self.username = match[1]

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
        self.wallpaper_id = match[1]

    def wallpapers(self):
        return (self.api.info(self.wallpaper_id),)
