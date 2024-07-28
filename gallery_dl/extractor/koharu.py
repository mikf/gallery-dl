# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://koharu.to/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?i)(?:https?://)?(?:koharu|anchira)\.to"


class KoharuGalleryExtractor(GalleryExtractor):
    """Extractor for koharu galleries"""
    category = "koharu"
    root = "https://koharu.to"
    root_api = "https://api.koharu.to"
    filename_fmt = "{num:>03}.{extension}"
    directory_fmt = ("{category}", "{id} {title}")
    archive_fmt = "{id}_{num}"
    pattern = BASE_PATTERN + r"/(?:g|reader)/(\d+)/(\w+)"
    example = "https://koharu.to/g/12345/67890abcde/"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_url = None

    def _init(self):
        self.headers = {
            "Accept" : "*/*",
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

        self.fmt = self.config("format")
        self.cbz = self.config("cbz", True)

        if self.cbz:
            self.filename_fmt = "{id} {title}.{extension}"
            self.directory_fmt = ("{category}",)

    def metadata(self, _):
        url = "{}/books/detail/{}/{}".format(
            self.root_api, self.groups[0], self.groups[1])
        self.data = data = self.request(url, headers=self.headers).json()
        data.pop("rels", None)
        data.pop("thumbnails", None)
        return data

    def images(self, _):
        data = self.data
        fmt = self._select_format(data["data"])

        url = "{}/books/data/{}/{}/{}/{}".format(
            self.root_api,
            data["id"], data["public_key"],
            fmt["id"], fmt["public_key"],
        )
        params = {
            "v": data["updated_at"],
            "w": fmt["w"],
        }

        if self.cbz:
            params["action"] = "dl"
            base = self.request(
                url, method="POST", params=params, headers=self.headers,
            ).json()["base"]
            url = "{}?v={}&w={}".format(base, data["updated_at"], fmt["w"])
            info = text.nameext_from_url(base)
            if not info["extension"]:
                info["extension"] = "cbz"
            return ((url, info),)

        data = self.request(url, params=params, headers=self.headers).json()
        base = data["base"]

        results = []
        for entry in data["entries"]:
            dimensions = entry["dimensions"]
            info = {"w": dimensions[0], "h": dimensions[1]}
            results.append((base + entry["path"], info))
        return results

    def _select_format(self, formats):
        if not self.fmt or self.fmt == "original":
            fmtid = "0"
        else:
            fmtid = str(self.fmt)

        try:
            fmt = formats[fmtid]
        except KeyError:
            raise exception.NotFoundError("format")

        fmt["w"] = fmtid
        return fmt


class KoharuSearchExtractor(Extractor):
    """Extractor for koharu search results"""
    category = "koharu"
    subcategory = "search"
    root = "https://koharu.to"
    root_api = "https://api.koharu.to"
    request_interval = (1.0, 2.0)
    pattern = BASE_PATTERN + r"/\?([^#]*)"
    example = "https://koharu.to/?s=QUERY"

    def _init(self):
        self.headers = {
            "Accept" : "*/*",
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

    def items(self):
        url_api = self.root_api + "/books"
        params = text.parse_query(self.groups[0])
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            data = self.request(
                url_api, params=params, headers=self.headers).json()

            try:
                entries = data["entries"]
            except KeyError:
                return

            for entry in entries:
                url = "{}/g/{}/{}/".format(
                    self.root, entry["id"], entry["public_key"])
                entry["_extractor"] = KoharuGalleryExtractor
                yield Message.Queue, url, entry

            try:
                if data["limit"] * data["page"] >= data["total"]:
                    return
            except Exception:
                pass
            params["page"] += 1
