# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://cyberdrop.me/"""

from . import lolisafe
from .common import Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?cyberdrop\.(?:me|to)"


class CyberdropAlbumExtractor(lolisafe.LolisafeAlbumExtractor):
    """Extractor for cyberdrop albums"""
    category = "cyberdrop"
    root = "https://cyberdrop.me"
    root_api = "https://api.cyberdrop.me"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://cyberdrop.me/a/ID"

    def items(self):
        files, data = self.fetch_album(self.album_id)

        yield Message.Directory, data
        for data["num"], file in enumerate(files, 1):
            file.update(data)
            text.nameext_from_url(file["name"], file)
            file["name"], sep, file["id"] = file["filename"].rpartition("-")
            yield Message.Url, file["url"], file

    def fetch_album(self, album_id):
        url = "{}/a/{}".format(self.root, album_id)
        page = self.request(url).text
        extr = text.extract_from(page)

        desc = extr('property="og:description" content="', '"')
        if desc.startswith("A privacy-focused censorship-resistant file "
                           "sharing platform free for everyone."):
            desc = ""
        extr('id="title"', "")

        album = {
            "album_id"   : album_id,
            "album_name" : text.unescape(extr('title="', '"')),
            "album_size" : text.parse_bytes(extr(
                '<p class="title">', "B")),
            "date"       : text.parse_datetime(extr(
                '<p class="title">', '<'), "%d.%m.%Y"),
            "description": text.unescape(text.unescape(  # double
                desc.rpartition(" [R")[0])),
        }

        file_ids = list(text.extract_iter(page, 'id="file" href="/f/', '"'))
        album["count"] = len(file_ids)
        return self._extract_files(file_ids), album

    def _extract_files(self, file_ids):
        for file_id in file_ids:
            try:
                url = "{}/api/file/info/{}".format(self.root_api, file_id)
                file = self.request(url).json()
                auth = self.request(file["auth_url"]).json()
                file["url"] = auth["url"]
            except Exception as exc:
                self.log.warning("%s (%s: %s)",
                                 file_id, exc.__class__.__name__, exc)
                continue

            yield file


class CyberdropMediaExtractor(CyberdropAlbumExtractor):
    """Extractor for cyberdrop media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"/f/([^/?#]+)"
    example = "https://cyberdrop.me/f/ID"

    def fetch_album(self, album_id):
        return self._extract_files((album_id,)), {
            "album_id"   : "",
            "album_name" : "",
            "album_size" : -1,
            "description": "",
            "count"      : 1,
        }
