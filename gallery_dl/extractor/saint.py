# -*- coding: utf-8 -*-

# Copyright 2024-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://saint2.su/ and https://turbovid.cr/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:turbo(?:vid)?\.cr|saint\d*\.(?:su|pk|cr|to))"


class SaintAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for saint albums"""
    category = "saint"
    root = "https://saint2.su"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://saint2.su/a/ID"

    def fetch_album(self, album_id):
        # album metadata
        response = self.request(self.root + "/a/" + album_id)
        extr = text.extract_from(response.text)

        title = extr("<title>", "</title")
        descr = extr('name="description" content="', '"/>')
        files = []

        while True:
            id2 = extr("/thumbs/", '"')
            if not id2:
                break

            id2, sep, ts = id2.rpartition(".")[0].rpartition("-")
            if sep:
                date = self.parse_timestamp(ts)
            else:
                date = None
                id2 = ts

            files.append({
                "id"   : extr("/embed/", '"'),
                "id2"  : id2,
                "date" : date,
                #  "extension": extr("<td>", "</"),
                "size" : text.parse_int(extr('data="', '"')),
                "file" : text.unescape(extr(
                    "onclick=\"play(", ")").strip("\"'")),
                "id_dl": extr("/d/", ")").rstrip("\"'"),
            })

        return files, {
            "album_id"     : album_id,
            "album_name"   : text.unescape(title.rpartition(" - ")[0]),
            "album_size"   : sum(file["size"] for file in files),
            "description"  : text.unescape(descr),
            "count"        : len(files),
            "_http_headers": {"Referer": response.url}
        }


class SaintMediaExtractor(SaintAlbumExtractor):
    """Extractor for saint media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"(/(embe)?d/([^/?#]+))"
    example = "https://saint2.su/embed/ID"

    def fetch_album(self, album_id):
        try:
            path, embed, _ = self.groups

            url = self.root + path
            response = self.request(url)
            extr = text.extract_from(response.text)

            if embed:
                id2, sep, ts = extr(
                    "/thumbs/", '"').rpartition(".")[0].rpartition("-")
                if sep:
                    date = self.parse_timestamp(ts)
                else:
                    date = None
                    id2 = ts

                file = {
                    "id"   : album_id,
                    "id2"  : id2,
                    "date" : date,
                    "file" : text.unescape(extr('<source src="', '"')),
                    "id_dl": extr("/d/", "'"),
                }

            else:  # /d/
                file = {
                    "file"     : text.unescape(extr('<a href="', '"')),
                    "id"       : album_id,
                    "id_dl"    : album_id,
                    "name"     : album_id,
                    "filename" : album_id,
                    "extension": "mp4",
                }

            file["_http_headers"] = {"Referer": response.url}
        except Exception as exc:
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            return (), {}

        return (file,), {
            "album_id"   : "",
            "album_name" : "",
            "album_size" : -1,
            "description": "",
            "count"      : 1,
        }
