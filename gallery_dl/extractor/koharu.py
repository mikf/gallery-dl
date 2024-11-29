# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://niyaniya.moe/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception
from ..cache import cache
import collections

BASE_PATTERN = (
    r"(?i)(?:https?://)?("
    r"(?:niyaniya|shupogaki)\.moe|"
    r"(?:koharu|anchira|seia)\.to|"
    r"(?:hoshino)\.one"
    r")"
)


class KoharuExtractor(Extractor):
    """Base class for koharu extractors"""
    category = "koharu"
    root = "https://niyaniya.moe"
    root_api = "https://api.schale.network"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.headers = {
            "Accept" : "*/*",
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

    def _pagination(self, endpoint, params):
        url_api = self.root_api + endpoint

        while True:
            data = self.request(
                url_api, params=params, headers=self.headers).json()

            try:
                entries = data["entries"]
            except KeyError:
                return

            for entry in entries:
                url = "{}/g/{}/{}".format(
                    self.root, entry["id"], entry["public_key"])
                entry["_extractor"] = KoharuGalleryExtractor
                yield Message.Queue, url, entry

            try:
                if data["limit"] * data["page"] >= data["total"]:
                    return
            except Exception:
                pass
            params["page"] += 1


class KoharuGalleryExtractor(KoharuExtractor, GalleryExtractor):
    """Extractor for koharu galleries"""
    filename_fmt = "{num:>03}.{extension}"
    directory_fmt = ("{category}", "{id} {title}")
    archive_fmt = "{id}_{num}"
    request_interval = 0.0
    pattern = BASE_PATTERN + r"/(?:g|reader)/(\d+)/(\w+)"
    example = "https://niyaniya.moe/g/12345/67890abcde/"

    TAG_TYPES = {
        0 : "general",
        1 : "artist",
        2 : "circle",
        3 : "parody",
        4 : "magazine",
        5 : "character",
        6 : "",
        7 : "uploader",
        8 : "male",
        9 : "female",
        10: "mixed",
        11: "language",
        12: "other",
    }

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
            self.root_api, self.groups[1], self.groups[2])
        self.data = data = self.request(url, headers=self.headers).json()
        data["date"] = text.parse_timestamp(data["created_at"] // 1000)

        tags = []
        types = self.TAG_TYPES
        tags_data = data["tags"]

        for tag in tags_data:
            name = tag["name"]
            namespace = tag.get("namespace", 0)
            tags.append(types[namespace] + ":" + name)
        data["tags"] = tags

        if self.config("tags", False):
            tags = collections.defaultdict(list)
            for tag in tags_data    :
                tags[tag.get("namespace", 0)].append(tag["name"])
            for type, values in tags.items():
                data["tags_" + types[type]] = values

        try:
            if self.cbz:
                data["count"] = len(data["thumbnails"]["entries"])
            del data["thumbnails"]
            del data["rels"]
        except Exception:
            pass

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
            info = {
                "w": dimensions[0],
                "h": dimensions[1],
                "_http_headers": self.headers,
            }
            results.append((base + entry["path"], info))
        return results

    def _select_format(self, formats):
        fmt = self.fmt

        if not fmt or fmt == "best":
            fmtids = ("0", "1600", "1280", "980", "780")
        elif isinstance(fmt, str):
            fmtids = fmt.split(",")
        elif isinstance(fmt, list):
            fmtids = fmt
        else:
            fmtids = (str(self.fmt),)

        for fmtid in fmtids:
            try:
                fmt = formats[fmtid]
                if fmt["id"]:
                    break
            except KeyError:
                self.log.debug("%s: Format %s is not available",
                               self.groups[1], fmtid)
        else:
            raise exception.NotFoundError("format")

        self.log.debug("%s: Selected format %s", self.groups[1], fmtid)
        fmt["w"] = fmtid
        return fmt


class KoharuSearchExtractor(KoharuExtractor):
    """Extractor for koharu search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/\?([^#]*)"
    example = "https://niyaniya.moe/?s=QUERY"

    def items(self):
        params = text.parse_query(self.groups[1])
        params["page"] = text.parse_int(params.get("page"), 1)
        return self._pagination("/books", params)


class KoharuFavoriteExtractor(KoharuExtractor):
    """Extractor for koharu favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/favorites(?:\?([^#]*))?"
    example = "https://niyaniya.moe/favorites"

    def items(self):
        self.login()

        params = text.parse_query(self.groups[1])
        params["page"] = text.parse_int(params.get("page"), 1)
        return self._pagination("/favorites", params)

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.headers["Authorization"] = \
                "Bearer " + self._login_impl(username, password)
            return

        raise exception.AuthenticationError("Username and password required")

    @cache(maxage=86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://auth.schale.network/login"
        data = {"uname": username, "passwd": password}
        response = self.request(
            url, method="POST", headers=self.headers, data=data)

        return response.json()["session"]
