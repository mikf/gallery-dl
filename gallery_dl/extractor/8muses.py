# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
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
    pattern = (r"(?:https?://)?(?:www\.)?8muses\.com"
               r"(/comics/album/[^?&#]+)(\?[^#]+)?")
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
                    "date"   : "dt:2018-07-10 00:00:00",
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
        ("https://www.8muses.com/comics/album/Fakku-Comics/8?sort=az", {
            "count": ">= 70",
            "keyword": {"name": r"re:^[R-Zr-z]"},
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)
        self.params = match.group(2) or ""

    def items(self):
        url = self.root + self.path + self.params

        while True:
            data = self._unobfuscate(text.extract(
                self.request(url).text,
                'id="ractive-public" type="text/plain">', '</script>')[0])

            images = data.get("pictures")
            if images:
                count = len(images)
                album = self._make_album(data["album"])
                yield Message.Directory, {"album": album, "count": count}
                for num, image in enumerate(images, 1):
                    url = self.root + "/image/fl/" + image["publicUri"]
                    img = {
                        "url"      : url,
                        "page"     : num,
                        "hash"     : image["publicUri"],
                        "count"    : count,
                        "album"    : album,
                        "extension": "jpg",
                    }
                    yield Message.Url, url, img

            albums = data.get("albums")
            if albums:
                for album in albums:
                    url = self.root + "/comics/album/" + album["permalink"]
                    album = {
                        "url"    : url,
                        "name"   : album["name"],
                        "private": album["isPrivate"],
                    }
                    yield Message.Queue, url, album

            if data["page"] >= data["pages"]:
                return
            path, _, num = self.path.rstrip("/").rpartition("/")
            path = path if num.isdecimal() else self.path
            url = "{}{}/{}{}".format(
                self.root, path, data["page"] + 1, self.params)

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
