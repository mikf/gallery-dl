# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comics.8muses.com/"""

from .common import Extractor, Message
from .. import text, util


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
    example = "https://comics.8muses.com/comics/album/PATH/TITLE"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)
        self.params = match.group(2) or ""

    def items(self):
        url = self.root + self.path + self.params

        while True:
            data = self._unobfuscate(text.extr(
                self.request(url).text,
                'id="ractive-public" type="text/plain">', '</script>'))

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
                    permalink = album.get("permalink")
                    if not permalink:
                        self.log.debug("Private album")
                        continue

                    url = self.root + "/comics/album/" + permalink
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
            "parts"  : album["path"].split("/"),
            "title"  : album["name"],
            "private": album["isPrivate"],
            "url"    : self.root + "/comics/album/" + album["permalink"],
            "parent" : text.parse_int(album["parentId"]),
            "views"  : text.parse_int(album["numberViews"]),
            "likes"  : text.parse_int(album["numberLikes"]),
            "date"   : text.parse_datetime(
                album["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
        }

    @staticmethod
    def _unobfuscate(data):
        return util.json_loads("".join([
            chr(33 + (ord(c) + 14) % 94) if "!" <= c <= "~" else c
            for c in text.unescape(data.strip("\t\n\r !"))
        ]))
