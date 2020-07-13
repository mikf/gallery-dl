# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wallhaven.cc/"""

from .common import Extractor, Message
from .. import text


class WallhavenExtractor(Extractor):
    """Base class for wallhaven extractors"""
    category = "wallhaven"
    filename_fmt = "{category}_{id}_{resolution}.{extension}"
    root = "https://wallhaven.cc"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = WallhavenAPI(self)


class WallhavenSearchExtractor(WallhavenExtractor):
    """Extractor for search results on wallhaven.cc"""
    subcategory = "search"
    directory_fmt = ("{category}", "{search[q]}")
    archive_fmt = "s_{search[q]}_{id}"
    pattern = r"(?:https?://)?wallhaven\.cc/search(?:/?\?([^/?#]+))?"
    test = (
        ("https://wallhaven.cc/search?q=touhou"),
        (("https://wallhaven.cc/search?q=id%3A87"
          "&categories=111&purity=100&sorting=date_added&order=asc&page=3"), {
            "pattern": r"https://w.wallhaven.cc/full/\w\w/wallhaven-\w+\.\w+",
            "count": "<= 20",
        }),
    )

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, {"search": self.params}
        for wp in self.api.search(self.params.copy()):
            wp["search"] = self.params
            yield Message.Url, wp["url"], wp


class WallhavenImageExtractor(WallhavenExtractor):
    """Extractor for individual wallpaper on wallhaven.cc"""
    subcategory = "image"
    archive_fmt = "{id}"
    pattern = (r"(?:https?://)?(?:wallhaven\.cc/w/|whvn\.cc/"
               r"|w\.wallhaven\.cc/[a-z]+/\w\w/wallhaven-)(\w+)")
    test = (
        ("https://wallhaven.cc/w/01w334", {
            "pattern": "https://[^.]+.wallhaven.cc/full/01/[^-]+-01w334.jpg",
            "content": "497212679383a465da1e35bd75873240435085a2",
            "keyword": {
                "id"         : "01w334",
                "width"      : 1920,
                "height"     : 1200,
                "resolution" : "1920x1200",
                "ratio"      : 1.6,
                "colors"     : list,
                "tags"       : list,
                "file_size"  : 278799,
                "file_type"  : "image/jpeg",
                "purity"     : "sfw",
                "short_url"  : "https://whvn.cc/01w334",
                "source"     : str,
                "uploader"   : {
                    "group"    : "Owner/Developer",
                    "username" : "AksumkA",
                },
                "date"       : "dt:2014-08-31 06:17:19",
                "wh_category": "anime",
                "views"      : int,
                "favorites"  : int,
            },
        }),
        # NSFW
        ("https://wallhaven.cc/w/dge6v3", {
            "url": "e4b802e70483f659d790ad5d0bd316245badf2ec",
        }),
        ("https://whvn.cc/01w334"),
        ("https://w.wallhaven.cc/full/01/wallhaven-01w334.jpg"),
    )

    def __init__(self, match):
        WallhavenExtractor.__init__(self, match)
        self.wallpaper_id = match.group(1)

    def items(self):
        data = self.api.info(self.wallpaper_id)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, data["url"], data


class WallhavenAPI():
    """Minimal interface to wallhaven's API"""

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
        url = "https://wallhaven.cc/api/v1/w/" + wallpaper_id
        return self._update(self._call(url)["data"])

    def search(self, params):
        url = "https://wallhaven.cc/api/v1/search"
        while True:
            data = self._call(url, params)
            yield from map(self._update, data["data"])
            if data["meta"]["current_page"] >= data["meta"]["last_page"]:
                return
            params["page"] = data["meta"]["current_page"] + 1

    def _call(self, url, params=None):
        return self.extractor.request(
            url, headers=self.headers, params=params).json()

    @staticmethod
    def _update(wp):
        width, _, height = wp["resolution"].partition("x")
        wp["url"] = wp.pop("path")
        if "tags" in wp:
            wp["tags"] = [t["name"] for t in wp["tags"]]
        wp["date"] = text.parse_datetime(
            wp.pop("created_at"), "%Y-%m-%d %H:%M:%S")
        wp["ratio"] = text.parse_float(wp["ratio"])
        wp["width"] = wp.pop("dimension_x")
        wp["height"] = wp.pop("dimension_y")
        wp["wh_category"] = wp["category"]
        return text.nameext_from_url(wp["url"], wp)
