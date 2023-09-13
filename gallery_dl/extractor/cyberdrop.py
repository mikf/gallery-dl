# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberdrop.me/"""

from . import lolisafe
from .. import text


class CyberdropAlbumExtractor(lolisafe.LolisafeAlbumExtractor):
    category = "cyberdrop"
    root = "https://cyberdrop.me"
    pattern = r"(?:https?://)?(?:www\.)?cyberdrop\.(?:me|to)/a/([^/?#]+)"
    example = "https://cyberdrop.me/a/ID"

    def fetch_album(self, album_id):
        url = self.root + "/a/" + self.album_id
        extr = text.extract_from(self.request(url).text)

        files = []
        append = files.append
        while True:
            url = text.unescape(extr('id="file" href="', '"'))
            if not url:
                break
            append({"file": url,
                    "_fallback": (self.root + url[url.find("/", 8):],)})

        return files, {
            "album_id"   : self.album_id,
            "album_name" : extr("name: '", "'"),
            "date"       : text.parse_timestamp(extr("timestamp: ", ",")),
            "album_size" : text.parse_int(extr("totalSize: ", ",")),
            "description": extr("description: `", "`"),
            "count"      : len(files),
        }
