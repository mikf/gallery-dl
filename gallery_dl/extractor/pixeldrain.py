# -*- coding: utf-8 -*-

# Copyright 2023-2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pixeldrain.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?pixeldrain\.com"


class PixeldrainExtractor(Extractor):
    """Base class for pixeldrain extractors"""
    category = "pixeldrain"
    root = "https://pixeldrain.com"
    archive_fmt = "{id}"

    def _init(self):
        api_key = self.config("api-key")
        if api_key:
            self.session.auth = util.HTTPBasicAuth("", api_key)

    def parse_datetime(self, date_string):
        return text.parse_datetime(
            date_string, "%Y-%m-%dT%H:%M:%S.%fZ")


class PixeldrainFileExtractor(PixeldrainExtractor):
    """Extractor for pixeldrain files"""
    subcategory = "file"
    filename_fmt = "{filename[:230]} ({id}).{extension}"
    pattern = BASE_PATTERN + r"/(?:u|api/file)/(\w+)"
    example = "https://pixeldrain.com/u/abcdefgh"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.file_id = match.group(1)

    def items(self):
        url = "{}/api/file/{}".format(self.root, self.file_id)
        file = self.request(url + "/info").json()

        file["url"] = url + "?download"
        file["date"] = self.parse_datetime(file["date_upload"])

        text.nameext_from_url(file["name"], file)
        yield Message.Directory, file
        yield Message.Url, file["url"], file


class PixeldrainAlbumExtractor(PixeldrainExtractor):
    """Extractor for pixeldrain albums"""
    subcategory = "album"
    directory_fmt = ("{category}",
                     "{album[date]:%Y-%m-%d} {album[title]} ({album[id]})")
    filename_fmt = "{num:>03} {filename[:230]} ({id}).{extension}"
    pattern = BASE_PATTERN + r"/(?:l|api/list)/(\w+)(?:#item=(\d+))?"
    example = "https://pixeldrain.com/l/abcdefgh"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)
        self.file_index = match.group(2)

    def items(self):
        url = "{}/api/list/{}".format(self.root, self.album_id)
        album = self.request(url).json()

        files = album["files"]
        album["count"] = album["file_count"]
        album["date"] = self.parse_datetime(album["date_created"])

        if self.file_index:
            idx = text.parse_int(self.file_index)
            try:
                files = (files[idx],)
            except LookupError:
                files = ()
        else:
            idx = 0

        del album["files"]
        del album["file_count"]

        yield Message.Directory, {"album": album}
        for num, file in enumerate(files, idx+1):
            file["album"] = album
            file["num"] = num
            file["url"] = url = "{}/api/file/{}?download".format(
                self.root, file["id"])
            file["date"] = self.parse_datetime(file["date_upload"])
            text.nameext_from_url(file["name"], file)
            yield Message.Url, url, file
