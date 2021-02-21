# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberdrop.me/"""

import base64

from .common import Extractor, Message
from .. import text


class CyberdropAlbumExtractor(Extractor):
    pattern = r"(?:https?://)?(?:www\.)?cyberdrop\.me/a/([^/]+)/?"
    category = "cyberdrop"
    subcategory = "album"
    directory_fmt = ("{category}", "{album}")
    root = "https://cyberdrop.me"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)
        self.album_url = self.root + "/a/" + self.album_id

    def items(self):
        initial_page = self.request(self.album_url).text

        albumName, _ = text.extract(initial_page, "name: '", "'")

        encodedFileList, _ = text.extract(initial_page, "fl: '", "'")

        fileList = [base64.b64decode(s.encode()).decode()
                    for s in encodedFileList.split(",")]

        for f in fileList:
            data = text.nameext_from_url(f)
            yield Message.Directory, {
                "album": self.album_id + ": " + albumName
            }
            yield Message.Url, "https://f.cyberdrop.cc/" + f, data
