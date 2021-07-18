# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pururin.to/"""

from .common import GalleryExtractor
from .. import text, util
import binascii
import json


class PururinGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on pururin.io"""
    category = "pururin"
    pattern = r"(?:https?://)?(?:www\.)?pururin\.[ti]o/(?:gallery|read)/(\d+)"
    test = (
        ("https://pururin.to/gallery/38661/iowant-2", {
            "pattern": r"https://cdn.pururin.[ti]o/\w+"
                       r"/images/data/\d+/\d+\.jpg",
            "keyword": {
                "title"     : "re:I ?owant 2!!",
                "title_en"  : "re:I ?owant 2!!",
                "title_jp"  : "",
                "gallery_id": 38661,
                "count"     : 19,
                "artist"    : ["Shoda Norihiro"],
                "group"     : ["Obsidian Order"],
                "parody"    : ["Kantai Collection"],
                "characters": ["Iowa", "Teitoku"],
                "tags"      : list,
                "type"      : "Doujinshi",
                "collection": "I owant you!",
                "convention": "C92",
                "rating"    : float,
                "uploader"  : "demo",
                "scanlator" : "mrwayne",
                "lang"      : "en",
                "language"  : "English",
            }
        }),
        ("https://pururin.to/gallery/7661/unisis-team-vanilla", {
            "count": 17,
        }),
        ("https://pururin.io/gallery/38661/iowant-2"),
    )
    root = "https://pururin.to"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/gallery/{}/x".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

        self._ext = ""
        self._cnt = 0

    def metadata(self, page):
        extr = text.extract_from(page)

        def _lst(key, e=extr):
            return [
                text.unescape(item)
                for item in text.extract_iter(e(key, "</td>"), 'title="', '"')
            ]

        def _str(key, e=extr):
            return text.unescape(text.extract(
                e(key, "</td>"), 'title="', '"')[0] or "")

        url = "{}/read/{}/01/x".format(self.root, self.gallery_id)
        page = self.request(url).text
        info = json.loads(binascii.a2b_base64(text.extract(
            page, '<gallery-read encoded="', '"')[0]).decode())
        self._ext = info["image_extension"]
        self._cnt = info["total_pages"]

        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : info["title"] or info.get("j_title") or "",
            "title_en"  : info["title"],
            "title_jp"  : info.get("j_title") or "",
            "artist"    : _lst("<td>Artist</td>"),
            "group"     : _lst("<td>Circle</td>"),
            "parody"    : _lst("<td>Parody</td>"),
            "tags"      : _lst("<td>Contents</td>"),
            "type"      : _str("<td>Category</td>"),
            "characters": _lst("<td>Character</td>"),
            "collection": _str("<td>Collection</td>"),
            "language"  : _str("<td>Language</td>"),
            "scanlator" : _str("<td>Scanlator</td>"),
            "convention": _str("<td>Convention</td>"),
            "uploader"  : text.remove_html(extr("<td>Uploader</td>", "</td>")),
            "rating"    : text.parse_float(extr(" :rating='"       , "'")),
        }
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, _):
        ufmt = "https://cdn.pururin.to/assets/images/data/{}/{{}}.{}".format(
            self.gallery_id, self._ext)
        return [(ufmt.format(num), None) for num in range(1, self._cnt + 1)]
