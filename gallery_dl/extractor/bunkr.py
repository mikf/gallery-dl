# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.is/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text
import json


class BunkrAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for bunkr.is albums"""
    category = "bunkr"
    root = "https://bunkr.is"
    pattern = r"(?:https?://)?(?:app\.)?bunkr\.(?:is|to)/a/([^/?#]+)"
    test = (
        ("https://bunkr.is/a/Lktg9Keq", {
            "pattern": r"https://cdn\.bunkr\.is/test-テスト-\"&>-QjgneIQv\.png",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
            "keyword": {
                "album_id": "Lktg9Keq",
                "album_name": 'test テスト "&>',
                "count": 1,
                "filename": 'test-テスト-"&>-QjgneIQv',
                "id": "QjgneIQv",
                "name": 'test-テスト-"&>',
                "num": int,
            },
        }),
        # mp4 (#2239)
        ("https://app.bunkr.is/a/ptRHaCn2", {
            "pattern": r"https://media-files\.bunkr\.is/_-RnHoW69L\.mp4",
            "content": "80e61d1dbc5896ae7ef9a28734c747b28b320471",
        }),
        # cdn4
        ("https://bunkr.is/a/iXTTc1o2", {
            "pattern": r"https://(cdn|media-files)4\.bunkr\.is/",
            "content": "da29aae371b7adc8c5ef8e6991b66b69823791e8",
        }),
        ("https://bunkr.to/a/Lktg9Keq"),
    )

    def fetch_album(self, album_id):
        if "//app." in self.root:
            return self._fetch_album_api(album_id)
        else:
            return self._fetch_album_site(album_id)

    def _fetch_album_api(self, album_id):
        files, data = LolisafeAlbumExtractor.fetch_album(self, album_id)

        for file in files:
            url = file["file"]
            if url.endswith(".mp4"):
                file["file"] = url.replace(
                    "//cdn.bunkr.is/", "//media-files.bunkr.is/", 1)
            else:
                file["_fallback"] = (url.replace("//cdn.", "//cdn3.", 1),)

        return files, data

    def _fetch_album_site(self, album_id):
        url = self.root + "/a/" + self.album_id

        try:
            data = json.loads(text.extract(
                self.request(url).text,
                'id="__NEXT_DATA__" type="application/json">', '<')[0])
            album = data["props"]["pageProps"]["album"]
            files = album["files"]
        except Exception as exc:
            self.log.debug(exc.__class__.__name__, exc)
            self.root = self.root.replace("bunkr", "app.bunkr", 1)
            return self._fetch_album_api(album_id)

        for file in files:
            name = file["name"]
            cdn = file["cdn"]
            if name.endswith((".mp4", ".m4v", ".mov")):
                cdn = cdn.replace("//cdn", "//media-files")
            file["file"] = cdn + "/" + name

        return files, {
            "album_id"   : self.album_id,
            "album_name" : text.unescape(album["name"]),
            "description": text.unescape(album["description"]),
            "count"      : len(files),
        }
