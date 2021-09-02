# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.net/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import collections
import json


class NhentaiBase():
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.net"
    media_url = "https://i.nhentai.net"


class NhentaiGalleryExtractor(NhentaiBase, GalleryExtractor):
    """Extractor for image galleries from nhentai.net"""
    pattern = r"(?:https?://)?nhentai\.net/g/(\d+)"
    test = ("https://nhentai.net/g/147850/", {
        "url": "5179dbf0f96af44005a0ff705a0ad64ac26547d0",
        "keyword": {
            "title"     : r"re:\[Morris\] Amazon no Hiyaku \| Amazon Elixir",
            "title_en"  : str,
            "title_ja"  : str,
            "gallery_id": 147850,
            "media_id"  : 867789,
            "count"     : 16,
            "date"      : 1446050915,
            "scanlator" : "",
            "artist"    : ["morris"],
            "group"     : list,
            "parody"    : list,
            "characters": list,
            "tags"      : list,
            "type"      : "manga",
            "lang"      : "en",
            "language"  : "English",
            "width"     : int,
            "height"    : int,
        },
    })

    def __init__(self, match):
        url = self.root + "/api/gallery/" + match.group(1)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        self.data = data = json.loads(page)

        title_en = data["title"].get("english", "")
        title_ja = data["title"].get("japanese", "")

        info = collections.defaultdict(list)
        for tag in data["tags"]:
            info[tag["type"]].append(tag["name"])

        language = ""
        for language in info["language"]:
            if language != "translated":
                language = language.capitalize()
                break

        return {
            "title"     : title_en or title_ja,
            "title_en"  : title_en,
            "title_ja"  : title_ja,
            "gallery_id": data["id"],
            "media_id"  : text.parse_int(data["media_id"]),
            "date"      : data["upload_date"],
            "scanlator" : data["scanlator"],
            "artist"    : info["artist"],
            "group"     : info["group"],
            "parody"    : info["parody"],
            "characters": info["character"],
            "tags"      : info["tag"],
            "type"      : info["category"][0] if info["category"] else "",
            "lang"      : util.language_to_code(language),
            "language"  : language,
        }

    def images(self, _):
        ufmt = "{}/galleries/{}/{{}}.{{}}".format(
            self.media_url, self.data["media_id"])
        extdict = {"j": "jpg", "p": "png", "g": "gif"}

        return [
            (ufmt.format(num, extdict.get(img["t"], "jpg")), {
                "width": img["w"], "height": img["h"],
            })
            for num, img in enumerate(self.data["images"]["pages"], 1)
        ]


class NhentaiSearchExtractor(NhentaiBase, Extractor):
    """Extractor for nhentai search results"""
    subcategory = "search"
    pattern = r"(?:https?://)?nhentai\.net/search/?\?([^#]+)"
    test = ("https://nhentai.net/search/?q=touhou", {
        "pattern": NhentaiGalleryExtractor.pattern,
        "count": 30,
        "range": "1-30",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def items(self):
        data = {"_extractor": NhentaiGalleryExtractor}
        for gallery_id in self._pagination(self.params):
            url = "{}/g/{}/".format(self.root, gallery_id)
            yield Message.Queue, url, data

    def _pagination(self, params):
        url = "{}/search/".format(self.root)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, 'href="/g/', '/')
            if 'class="next"' not in page:
                return
            params["page"] += 1


class NhentaiFavoriteExtractor(NhentaiBase, Extractor):
    """Extractor for nhentai favorites"""
    subcategory = "favorite"
    pattern = r"(?:https?://)?nhentai\.net/favorites/?(?:\?([^#]+))?"
    test = ("https://nhentai.net/favorites/",)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def items(self):
        data = {"_extractor": NhentaiGalleryExtractor}
        for gallery_id in self._pagination(self.params):
            url = "{}/g/{}/".format(self.root, gallery_id)
            yield Message.Queue, url, data

    def _pagination(self, params):
        url = "{}/favorites/".format(self.root)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, 'href="/g/', '/')
            if 'class="next"' not in page:
                return
            params["page"] += 1
