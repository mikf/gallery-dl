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
    "bunkr": {
        "root": "https://app.bunkr.is",
        "pattern": r"(?:app\.)?bunkr\.(?:is|to)",
    },
    "zzzz" : {
        "root": "https://zz.ht",
        "pattern": r"zz\.(?:ht|fo)",
    },
})


class LolisafeAlbumExtractor(LolisafeExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + "/a/([^/?#]+)"
    test = (
        ("https://app.bunkr.is/a/Lktg9Keq", {
            "pattern": r"https://cdn\.bunkr\.is/test-テスト-\"&>-QjgneIQv\.png",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
            "keyword": {
                "album_id": "Lktg9Keq",
                "album_name": 'test テスト "&>',
                "count": 1,
                "filename": 'test-テスト-"&>-QjgneIQv',
                "id": "QjgneIQv",
                "name": 'test-テスト-"&>',
                "num": int,
            },
        }),
        # mp4 (#2239)
        ("https://bunkr.is/a/ptRHaCn2", {
            "pattern": r"https://media-files\.bunkr\.is/_-RnHoW69L\.mp4",
            "content": "80e61d1dbc5896ae7ef9a28734c747b28b320471",
        }),
        ("https://bunkr.to/a/Lktg9Keq"),
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
            if self.category == "bunkr":
                self.root = "https://app.bunkr.is"
            else:
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

            if data["extension"] == "mp4":
                url = url.replace(
                    "//cdn.bunkr.is/", "//media-files.bunkr.is/", 1)
            yield Message.Url, url, data

    def fetch_album(self, album_id):
        url = "{}/api/album/get/{}".format(self.root, album_id)
        data = self.request(url).json()

        return data["files"], {
            "album_id"  : self.album_id,
            "album_name": text.unescape(data["title"]),
            "count"     : data["count"],
        }
