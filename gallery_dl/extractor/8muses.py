# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comics.8muses.com/"""

from .common import Extractor, Message
from .. import text
import json


class _8musesAlbumExtractor(Extractor):
    """Extractor for image albums on comics.8muses.com"""
    category = "8muses"
    subcategory = "album"
    directory_fmt = ("{category}", "{album[path]}")
    filename_fmt = "{page:>03}.{extension}"
    archive_fmt = "{hash}"
    root = "https://comics.8muses.com"
    pattern = (r"(?:https?://)?(?:comics\.|www\.)?8muses\.com"
               r"(/comics/album/[^?#]+)(\?[^#]+)?")
    test = (
        ("https://comics.8muses.com/comics/album/Fakku-Comics/mogg/Liar", {
            "url": "6286ac33087c236c5a7e51f8a9d4e4d5548212d4",
            "pattern": r"https://comics.8muses.com/image/fl/[\w-]+",
            "keyword": {
                "url"  : str,
                "hash" : str,
                "page" : int,
                "count": 6,
                "album": {
                    "id"     : 10467,
                    "title"  : "Liar",
                    "path"   : "Fakku Comics/mogg/Liar",
                    "private": False,
                    "url"    : str,
                    "parent" : 10464,
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
        # custom sorting
        ("https://www.8muses.com/comics/album/Fakku-Comics/11?sort=az", {
            "count": ">= 70",
            "keyword": {"name": r"re:^[R-Zr-z]"},
        }),
        # non-ASCII characters
        (("https://comics.8muses.com/comics/album/Various-Authors/Chessire88"
          "/From-Trainers-to-Pokmons"), {
            "count": 2,
            "keyword": {"name": "re:From Trainers to Pokémons"},
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
                    yield Message.Queue, url, {
                        "url"       : url,
                        "name"      : album["name"],
                        "private"   : album["isPrivate"],
                        "_extractor": _8musesAlbumExtractor,
                    }

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
            chr(33 + (ord(c) + 14) % 94) if "!" <= c <= "~" else c
            for c in text.unescape(data.strip("\t\n\r !"))
        ]))
