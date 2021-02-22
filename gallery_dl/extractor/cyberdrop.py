# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberdrop.me/"""

from .common import Extractor, Message
from .. import text
import base64


class CyberdropAlbumExtractor(Extractor):
    category = "cyberdrop"
    subcategory = "album"
    root = "https://cyberdrop.me"
    directory_fmt = ("{category}", "{album_id} {album_name}")
    archive_fmt = "{album_id}_{id}"
    pattern = r"(?:https?://)?(?:www\.)?cyberdrop\.me/a/([^/?#]+)"
    test = ("https://cyberdrop.me/a/keKRjm4t", {
        "pattern": r"https://f\.cyberdrop\.cc/.*\.[a-z]+$",
        "keyword": {
            "album_id": "keKRjm4t",
            "album_name": "Fate (SFW)",
            "album_size": 150069254,
            "count": 62,
            "date": "dt:2020-06-18 13:14:20",
            "description": "",
            "id": r"re:\w{8}",
        },
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)

    def items(self):
        url = self.root + "/a/" + self.album_id
        extr = text.extract_from(self.request(url).text)
        extr("const albumData = {", "")

        data = {
            "album_id"   : self.album_id,
            "album_name" : extr("name: '", "'"),
            "date"       : text.parse_timestamp(extr("timestamp: ", ",")),
            "album_size" : text.parse_int(extr("totalSize: ", ",")),
            "description": extr("description: `", "`"),
        }
        files = extr("fl: '", "'").split(",")
        data["count"] = len(files)

        yield Message.Directory, data
        for file_b64 in files:
            file = base64.b64decode(file_b64.encode()).decode()
            text.nameext_from_url(file, data)
            data["filename"], _, data["id"] = data["filename"].rpartition("-")
            yield Message.Url, "https://f.cyberdrop.cc/" + file, data
