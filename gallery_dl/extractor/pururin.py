# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pururin.io/"""

from .common import GalleryExtractor
from .. import text, util
import json


class PururinGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on pururin.io"""
    category = "pururin"
    pattern = r"(?:https?://)?(?:www\.)?pururin\.io/(?:gallery|read)/(\d+)"
    test = ("https://pururin.io/gallery/38661/iowant-2", {
        "pattern": r"https://cdn.pururin.io/assets/images/data/38661/\d+\.jpg",
        "keyword": {
            "title"     : "Iowant 2!!",
            "title_en"  : "Iowant 2!!",
            "title_jp"  : "",
            "gallery_id": 38661,
            "count"     : 19,
            "artist"    : ["Shoda Norihiro"],
            "group"     : ["Obsidian Order"],
            "parody"    : ["Kantai Collection"],
            "characters": ["Iowa", "Teitoku"],
            "tags"      : list,
            "type"      : "Doujinshi",
            "collection": "",
            "convention": "C92",
            "rating"    : float,
            "uploader"  : "demo",
            "scanlator" : "",
            "lang"      : "en",
            "language"  : "English",
        }
    })
    root = "https://pururin.io"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/gallery/{}/x".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

        self._ext = ""
        self._cnt = 0

    def metadata(self, page):
        data = text.extract_all(page, (
            ("artist"    , "<td>Artist</td>"    , "</td>"),
            ("group"     , "<td>Circle</td>"    , "</td>"),
            ("parody"    , "<td>Parody</td>"    , "</td>"),
            ("tags"      , "<td>Contents</td>"  , "</td>"),
            ("type"      , "<td>Category</td>"  , "</td>"),
            ("characters", "<td>Character</td>" , "</td>"),
            ("collection", "<td>Collection</td>", "</td>"),
            ("language"  , "<td>Language</td>"  , "</td>"),
            ("scanlator" , "<td>Scanlator</td>" , "</td>"),
            ("convention", "<td>Convention</td>", "</td>"),
            ("uploader"  , "<td>Uploader</td>"  , "</td>"),
            ("rating"    , " :rating='"         , "'"),
        ))[0]

        url = "{}/read/{}/01/x".format(self.root, self.gallery_id)
        page = self.request(url).text
        info = json.loads(text.unescape(text.extract(
            page, ':gallery="', '"')[0]))

        self._ext = info["image_extension"]
        self._cnt = info["total_pages"]

        for key in ("artist", "group", "parody", "tags", "characters"):
            data[key] = [
                text.unescape(item)
                for item in text.extract_iter(data[key], 'title="', '"')
            ]
        for key in ("type", "collection", "language", "scanlator",
                    "convention"):
            data[key] = text.unescape(text.extract(
                data[key], 'title="', '"')[0] or "")

        data["gallery_id"] = text.parse_int(self.gallery_id)
        data["title"] = info["title"] or info.get("j_title") or ""
        data["title_en"] = info["title"]
        data["title_jp"] = info.get("j_title") or ""
        data["uploader"] = text.remove_html(data["uploader"])
        data["rating"] = text.parse_float(data["rating"])
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, _):
        ufmt = "https://cdn.pururin.io/assets/images/data/{}/{{}}.{}".format(
            self.gallery_id, self._ext)
        return [(ufmt.format(num), None) for num in range(1, self._cnt + 1)]
