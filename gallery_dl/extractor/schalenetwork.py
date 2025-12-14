# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://niyaniya.moe/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception
import collections

BASE_PATTERN = (
    r"(?i)(?:https?://)?("
    r"(?:niyaniya|shupogaki)\.moe|"
    r"(?:koharu|anchira|seia)\.to|"
    r"(?:hoshino)\.one"
    r")"
)


class SchalenetworkExtractor(Extractor):
    """Base class for schale.network extractors"""
    category = "schalenetwork"
    root = "https://niyaniya.moe"
    root_api = "https://api.schale.network"
    root_auth = "https://auth.schale.network"
    extr_class = None
    request_interval = (0.5, 1.5)

    def _init(self):
        self.headers = {
            "Accept" : "*/*",
            "Referer": self.root + "/",
            "Origin" : self.root,
        }

    def _pagination(self, endpoint, params):
        url_api = self.root_api + endpoint
        cls = self.extr_class

        while True:
            data = self.request_json(
                url_api, params=params, headers=self.headers)

            try:
                entries = data["entries"]
            except KeyError:
                return

            for entry in entries:
                url = f"{self.root}/g/{entry['id']}/{entry['key']}"
                entry["_extractor"] = cls
                yield Message.Queue, url, entry

            try:
                if data["limit"] * data["page"] >= data["total"]:
                    return
            except Exception:
                pass
            params["page"] += 1

    def _token(self, required=True):
        if token := self.config("token"):
            return f"Bearer {token.rpartition(' ')[2]}"
        if required:
            raise exception.AuthRequired("'token'", "your favorites")

    def _crt(self):
        crt = self.config("crt")
        if not crt:
            self._require_auth()

        if not text.re(r"^[0-9a-f-]+$").match(crt):
            path, _, qs = crt.partition("?")
            if not qs:
                qs = path
            crt = text.parse_query(qs).get("crt")
            if not crt:
                self._require_auth()

        return crt

    def _require_auth(self, exc=None):
        if exc is None:
            msg = None
        else:
            msg = f"{exc.status} {exc.response.reason}"
        raise exception.AuthRequired(
            "'crt' query parameter & matching 'user-agent'", None, msg)


class SchalenetworkGalleryExtractor(SchalenetworkExtractor, GalleryExtractor):
    """Extractor for schale.network galleries"""
    filename_fmt = "{num:>03}.{extension}"
    directory_fmt = ("{category}", "{id} {title}")
    archive_fmt = "{id}_{num}"
    request_interval = 0.0
    pattern = rf"{BASE_PATTERN}/(?:g|reader)/(\d+)/(\w+)"
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
        13: "reclass",
    }

    def metadata(self, _):
        _, gid, gkey = self.groups

        url = f"{self.root_api}/books/detail/{gid}/{gkey}"
        headers = self.headers
        data = self.request_json(url, headers=headers)

        try:
            data["date"] = self.parse_timestamp(data["created_at"] // 1000)
            data["count"] = len(data["thumbnails"]["entries"])
            del data["thumbnails"]
        except Exception:
            pass

        tags = []
        types = self.TAG_TYPES
        for tag in data["tags"]:
            name = tag["name"]
            namespace = tag.get("namespace", 0)
            tags.append(types[namespace] + ":" + name)
        if self.config("tags", False):
            categories = collections.defaultdict(list)
            for tag in data["tags"]:
                categories[tag.get("namespace", 0)].append(tag["name"])
            for type, values in categories.items():
                data["tags_" + types[type]] = values
        data["tags"] = tags

        url = f"{self.root_api}/books/detail/{gid}/{gkey}?crt={self._crt()}"
        if token := self._token(False):
            headers = headers.copy()
            headers["Authorization"] = token
        try:
            data_fmt = self.request_json(
                url, method="POST", headers=headers)
        except exception.HttpError as exc:
            self._require_auth(exc)

        self.fmt = self._select_format(data_fmt["data"])
        data["source"] = data_fmt.get("source")

        return data

    def images(self, _):
        _, gid, gkey = self.groups
        fmt = self.fmt

        url = (f"{self.root_api}/books/data/{gid}/{gkey}"
               f"/{fmt['id']}/{fmt['key']}/{fmt['w']}?crt={self._crt()}")
        headers = self.headers

        if self.config("cbz", False):
            headers["Authorization"] = self._token()
            dl = self.request_json(
                f"{url}&action=dl", method="POST", headers=headers)
            # 'crt' parameter here is necessary for 'hdoujin' downloads
            url = f"{dl['base']}?crt={self._crt()}"
            info = text.nameext_from_url(url)
            if "fallback" in dl:
                info["_fallback"] = (dl["fallback"],)
            if not info["extension"]:
                info["extension"] = "cbz"
            return ((url, info),)

        data = self.request_json(url, headers=headers)
        base = data["base"]

        results = []
        for entry in data["entries"]:
            dimensions = entry["dimensions"]
            info = {
                "width" : dimensions[0],
                "height": dimensions[1],
                "_http_headers": headers,
            }
            results.append((base + entry["path"], info))
        return results

    def _select_format(self, formats):
        fmt = self.config("format")

        if not fmt or fmt == "best":
            fmtids = ("0", "1600", "1280", "980", "780")
        elif isinstance(fmt, str):
            fmtids = fmt.split(",")
        elif isinstance(fmt, list):
            fmtids = fmt
        else:
            fmtids = (str(fmt),)

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


class SchalenetworkSearchExtractor(SchalenetworkExtractor):
    """Extractor for schale.network search results"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/(?:tag/([^/?#]+)|browse)?(?:/?\?([^#]*))?$"
    example = "https://niyaniya.moe/browse?s=QUERY"

    def items(self):
        _, tag, qs = self.groups

        params = text.parse_query(qs)
        params["page"] = text.parse_int(params.get("page"), 1)

        if tag is not None:
            ns, sep, tag = text.unquote(tag).partition(":")
            if "+" in tag:
                tag = tag.replace("+", " ")
                q = '"'
            else:
                q = ""
            q = '"' if " " in tag else ""
            params["s"] = f"{ns}{sep}{q}^{tag}${q}"

        return self._pagination("/books", params)


class SchalenetworkFavoriteExtractor(SchalenetworkExtractor):
    """Extractor for schale.network favorites"""
    subcategory = "favorite"
    pattern = rf"{BASE_PATTERN}/favorites(?:\?([^#]*))?"
    example = "https://niyaniya.moe/favorites"

    def items(self):
        params = text.parse_query(self.groups[1])
        params["page"] = text.parse_int(params.get("page"), 1)
        self.headers["Authorization"] = self._token()
        return self._pagination(f"/books/favorites?crt={self._crt()}", params)


SchalenetworkExtractor.extr_class = SchalenetworkGalleryExtractor
