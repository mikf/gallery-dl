# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberdrop.me/"""

from .common import Extractor, Message
from .. import text


class CyberdropAlbumExtractor(Extractor):
    category = "cyberdrop"
    subcategory = "album"
    root = "https://cyberdrop.me"
    directory_fmt = ("{category}", "{album_name} ({album_id})")
    archive_fmt = "{album_id}_{id}"
    pattern = r"(?:https?://)?(?:www\.)?cyberdrop\.me/a/([^/?#]+)"
    test = (
        # images
        ("https://cyberdrop.me/a/keKRjm4t", {
            "pattern": r"https://fs-\d+\.cyberdrop\.to/.*\.(jpg|png|webp)$",
            "keyword": {
                "album_id": "keKRjm4t",
                "album_name": "Fate (SFW)",
                "album_size": 150069254,
                "count": 62,
                "date": "dt:2020-06-18 13:14:20",
                "description": "",
                "id": r"re:\w{8}",
            },
        }),
        # videos
        ("https://cyberdrop.me/a/l8gIAXVD", {
            "pattern": r"https://fs-\d+\.cyberdrop\.to/.*\.mp4$",
            "count": 31,
            "keyword": {
                "album_id": "l8gIAXVD",
                "album_name": "Achelois17 videos",
                "album_size": 652037121,
                "date": "dt:2020-06-16 15:40:44",
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        url = self.root + "/a/" + self.album_id
        extr = text.extract_from(self.request(url).text)

        files = []
        append = files.append
        while True:
            url = extr('id="file" href="', '"')
            if not url:
                break
            append(text.unescape(url))

        data = {
            "album_id"   : self.album_id,
            "album_name" : extr("name: '", "'"),
            "date"       : text.parse_timestamp(extr("timestamp: ", ",")),
            "album_size" : text.parse_int(extr("totalSize: ", ",")),
            "description": extr("description: `", "`"),
            "count"      : len(files),
        }

        yield Message.Directory, data
        for url in files:
            text.nameext_from_url(url, data)
            data["filename"], _, data["id"] = data["filename"].rpartition("-")
            yield Message.Url, url, data
