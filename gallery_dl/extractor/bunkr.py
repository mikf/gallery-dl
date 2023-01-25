# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.ru/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text
import json


class BunkrAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for bunkr.ru albums"""
    category = "bunkr"
    root = "https://bunkr.ru"
    pattern = r"(?:https?://)?(?:app\.)?bunkr\.(?:ru|is|to)/a/([^/?#]+)"
    test = (
        ("https://bunkr.ru/a/Lktg9Keq", {
            "pattern": r"https://cdn\.bunkr\.ru/test-テスト-\"&>-QjgneIQv\.png",
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
            "pattern": r"https://media-files\.bunkr\.ru/_-RnHoW69L\.mp4",
            "content": "80e61d1dbc5896ae7ef9a28734c747b28b320471",
        }),
        # cdn4
        ("https://bunkr.is/a/iXTTc1o2", {
            "pattern": r"https://(cdn|media-files)4\.bunkr\.ru/",
            "content": "da29aae371b7adc8c5ef8e6991b66b69823791e8",
        }),
        ("https://bunkr.to/a/Lktg9Keq"),
    )

    def fetch_album(self, album_id):
        root = self.root

        try:
            data = json.loads(text.extr(
                self.request(root + "/a/" + self.album_id).text,
                'id="__NEXT_DATA__" type="application/json">', '<'))
            album = data["props"]["pageProps"]["album"]
            files = album["files"]
        except Exception as exc:
            self.log.debug("%s: %s", exc.__class__.__name__, exc)
            self.log.debug("Falling back to lolisafe API")
            self.root = root.replace("://", "://app.", 1)
            files, data = LolisafeAlbumExtractor.fetch_album(self, album_id)
            # fix file URLs (bunkr..ru -> bunkr.ru) (#3481)
            for file in files:
                file["file"] = file["file"].replace("bunkr..", "bunkr.", 1)
        else:
            for file in files:
                file["file"] = file["cdn"] + "/" + file["name"]
            data = {
                "album_id"   : self.album_id,
                "album_name" : text.unescape(album["name"]),
                "description": text.unescape(album["description"]),
                "count"      : len(files),
            }

        headers = {"Referer": root.replace("://", "://stream.", 1) + "/"}
        for file in files:
            if file["file"].endswith(
                    (".mp4", ".m4v", ".mov", ".webm", ".mkv", ".ts",
                     ".zip", ".rar", ".7z")):
                file["_http_headers"] = headers
                file["file"] = file["file"].replace(
                    "://cdn", "://media-files", 1)

        return files, data
