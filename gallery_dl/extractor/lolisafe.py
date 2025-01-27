# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for lolisafe/chibisafe instances"""

from .common import BaseExtractor, Message
from .. import text


class LolisafeExtractor(BaseExtractor):
    """Base class for lolisafe extractors"""
    basecategory = "lolisafe"
    directory_fmt = ("{category}", "{album_name} ({album_id})")
    archive_fmt = "{album_id}_{id}"


BASE_PATTERN = LolisafeExtractor.update({
})


class LolisafeAlbumExtractor(LolisafeExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + "/a/([^/?#]+)"
    example = "https://xbunkr.com/a/ID"

    def __init__(self, match):
        LolisafeExtractor.__init__(self, match)
        self.album_id = self.groups[-1]

    def _init(self):
        domain = self.config("domain")
        if domain == "auto":
            self.root = text.root_from_url(self.url)
        elif domain:
            self.root = text.ensure_http_scheme(domain)

    def items(self):
        files, data = self.fetch_album(self.album_id)

        yield Message.Directory, data
        for data["num"], file in enumerate(files, 1):
            url = file["file"]
            file.update(data)

            if "extension" not in file:
                text.nameext_from_url(url, file)

            if "name" in file:
                name = file["name"]
                file["name"] = name.rpartition(".")[0] or name
                _, sep, fid = file["filename"].rpartition("-")
                if not sep or len(fid) == 12:
                    if "id" not in file:
                        file["id"] = ""
                    file["filename"] = file["name"]
                else:
                    file["id"] = fid
                    file["filename"] = file["name"] + "-" + fid
            elif "id" in file:
                file["name"] = file["filename"]
                file["filename"] = "{}-{}".format(file["name"], file["id"])
            else:
                file["name"], sep, file["id"] = \
                    file["filename"].rpartition("-")

            yield Message.Url, url, file

    def fetch_album(self, album_id):
        url = "{}/api/album/get/{}".format(self.root, album_id)
        data = self.request(url).json()

        return data["files"], {
            "album_id"  : self.album_id,
            "album_name": text.unescape(data["title"]),
            "count"     : data["count"],
        }
