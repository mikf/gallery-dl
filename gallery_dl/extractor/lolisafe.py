# -*- coding: utf-8 -*-

# Copyright 2021-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for lolisafe/chibisafe instances"""

from .common import BaseExtractor, Message
from .. import text


class LolisafeExtractor(BaseExtractor):
    """Base class for lolisafe extractors"""
    basecategory = "lolisafe"
    directory_fmt = ("{category}", "{album_name} ({album_id})")
    archive_fmt = "{album_id}_{id}"


BASE_PATTERN = LolisafeExtractor.update({
    "zzzz" : {
        "root": "https://zz.ht",
        "pattern": r"zz\.(?:ht|fo)",
    },
})


class LolisafeAlbumExtractor(LolisafeExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + "/a/([^/?#]+)"
    test = (
        ("https://zz.ht/a/lop7W6EZ", {
            "pattern": r"https://z\.zz\.fo/(4anuY|ih560)\.png",
            "count": 2,
            "keyword": {
                "album_id": "lop7W6EZ",
                "album_name": "ferris",
            },
        }),
        ("https://zz.fo/a/lop7W6EZ"),
    )

    def __init__(self, match):
        LolisafeExtractor.__init__(self, match)
        self.album_id = match.group(match.lastindex)

        domain = self.config("domain")
        if domain is None or domain == "auto":
            self.root = text.root_from_url(match.group(0))
        else:
            self.root = text.ensure_http_scheme(domain)

    def items(self):
        files, data = self.fetch_album(self.album_id)

        yield Message.Directory, data
        for data["num"], file in enumerate(files, 1):
            url = file["file"]
            if "_fallback" in file:
                data["_fallback"] = file["_fallback"]
            text.nameext_from_url(url, data)
            data["name"], sep, data["id"] = data["filename"].rpartition("-")
            yield Message.Url, url, data

    def fetch_album(self, album_id):
        url = "{}/api/album/get/{}".format(self.root, album_id)
        data = self.request(url).json()

        return data["files"], {
            "album_id"  : self.album_id,
            "album_name": text.unescape(data["title"]),
            "count"     : data["count"],
        }
