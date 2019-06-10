# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.8muses.com/"""

from .common import Extractor, Message
from .. import text
import json


class _8musesAlbumExtractor(Extractor):
    """Extractor for image albums on www.8muses.com"""
    category = "8muses"
    subcategory = "album"
    directory_fmt = ("{category}", "{album[path]}")
    filename_fmt = "{page:>03}.{extension}"
    archive_fmt = "{hash}"
    root = "https://www.8muses.com"
    pattern = r"(?:https?://)?(?:www\.)?8muses\.com(/comics/album/[^?&#]+)"
    test = (
        ("https://www.8muses.com/comics/album/Fakku-Comics/santa/Im-Sorry", {
            "url": "82449d6a26a29204695cba5d52c3ec60170bc159",
            "keyword": {
                "url"  : str,
                "hash" : str,
                "page" : int,
                "count": 16,
                "album": {
                    "id"     : 10457,
                    "title"  : "Im Sorry",
                    "path"   : "Fakku Comics/santa/Im Sorry",
                    "private": False,
                    "url"    : str,
                    "parent" : 10454,
                    "views"  : int,
                    "likes"  : int,
                    "date"   : "type:datetime",
                },
            },
        }),
        ("https://www.8muses.com/comics/album/Fakku-Comics/santa", {
            "count": ">= 3",
            "pattern": pattern,
            "keyword": {
                "url"    : str,
                "name"   : str,
                "private": False,
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)

    def items(self):
        data = self._unobfuscate(text.extract(
            self.request(self.root + self.path).text,
            '<script id="ractive-public" type="text/plain">', '</script>')[0])

        if data.get("pictures"):
            images = data["pictures"]
            album = self._make_album(data["album"])
            yield Message.Directory, {"album": album, "count": len(images)}
            for num, image in enumerate(images, 1):
                url = self.root + "/image/fl/" + image["publicUri"]
                img = {
                    "url"      : url,
                    "page"     : num,
                    "hash"     : image["publicUri"],
                    "count"    : len(images),
                    "album"    : album,
                    "extension": "jpg",
                }
                yield Message.Url, url, img

        if data.get("albums"):
            for album in data["albums"]:
                url = self.root + "/comics/album/" + album["permalink"]
                album = {
                    "url"    : url,
                    "name"   : album["name"],
                    "private": album["isPrivate"],
                }
                yield Message.Queue, url, album

    def _make_album(self, album):
        return {
            "id"     : album["id"],
            "path"   : album["path"],
            "title"  : album["name"],
            "private": album["isPrivate"],
            "url"    : self.root + album["permalink"],
            "parent" : text.parse_int(album["parentId"]),
            "views"  : text.parse_int(album["numberViews"]),
            "likes"  : text.parse_int(album["numberLikes"]),
            "date"   : text.parse_datetime(
                album["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    @staticmethod
    def _unobfuscate(data):
        return json.loads("".join([
            chr(33 + (ord(c) + 14) % 94) if c != " " else c
            for c in text.unescape(data.strip("\t\n\r !"))
        ]))
