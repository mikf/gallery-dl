# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imageshack.com/"""

from .common import Extractor, Message
from .. import text
import time

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imageshack\.com"


class ImageshackExtractor(Extractor):
    """Base class for imageshack extractors"""
    category = "imageshack"
    root = "https://imageshack.com"
    directory_fmt = ("{category}", "{owner[username]}")
    filename_fmt = "{date:%Y-%m-%d} {id}{title:? - //[:230]}.{extension}"
    archive_fmt = "{id}"
    offset = 0

    def items(self):
        for img in self.images():
            img["date"] = self.parse_timestamp(img["creation_date"])
            url = text.ensure_http_scheme(img["direct_link"])

            if name := img["original_filename"]:
                text.nameext_from_name(name, img)
                if not img["extension"]:
                    img["extension"] = text.ext_from_url(url)
            else:
                text.nameext_from_url(url, img)

            yield Message.Directory, "", img
            yield Message.Url, url, img

    def request_api(self, endpoint, params):
        url = f"{self.root}/rest_api/{endpoint}"
        params["ts"] = int(time.time())
        headers = {
            "Accept"        : "application/json, text/javascript, */*; q=0.01",
            "Content-Type"  : "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority"      : "u=0",
        }
        return self.request_json(url, params=params, headers=headers)["result"]

    def _pagination(self, endpoint, params, callback=None):
        while True:
            data = self.request_api(endpoint, params)

            if callback is not None:
                callback(data)
                callback = None
            self.kwdict["total"] = total = data.get("total")

            yield from data["images"]

            try:
                if data["offset"] >= total:
                    break
            except Exception as exc:
                self.log.traceback(exc)
                break
            params["offset"] += params["limit"]

    def skip_posts(self, n):
        self.offset += n
        return n

    skip_files = skip_posts


class ImageshackImageExtractor(ImageshackExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/i/([^/?#]+)"
    example = "https://imageshack.com/i/ID"

    def images(self):
        img = self.request_api("/v2/images/" + self.groups[0], {})
        return (img,)

    skip_files = skip_posts = None


class ImageshackGalleryExtractor(ImageshackExtractor):
    subcategory = "gallery"
    directory_fmt = ("{category}", "{owner[username]}",
                     "{gallery[title]} ({gallery[id]})")
    archive_fmt = "{gallery[id]}/{id}"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://imageshack.com/a/ID"

    def images(self):
        return self._pagination("/v2/albums/" + self.groups[0], {
            "limit"       : 40,
            "offset"      : self.offset,
            "hide_empty"  : "true",
            "show_private": "false",
        }, self._parse_gallery)

    def _parse_gallery(self, data):
        self.kwdict["gallery"] = {
            "id"         : data.get("id"),
            "title"      : data.get("title"),
            "description": data.get("description"),
            "owner"      : data.get("owner"),
            "date"       : self.parse_timestamp(data.get("creation_date")),
        }


class ImageshackUserExtractor(ImageshackExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?#]+)"
    example = "https://imageshack.com/user/USER"

    def images(self):
        return self._pagination("/v2/images", {
            "username"  : self.groups[0],
            "limit"     : 40,
            "offset"    : self.offset,
            "hide_empty": "true",
        })
