# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://nhentai.net/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import collections
import random


class NhentaiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from nhentai.net"""
    category = "nhentai"
    root = "https://nhentai.net"
    pattern = r"(?:https?://)?nhentai\.net/g/(\d+)"
    example = "https://nhentai.net/g/12345/"

    def __init__(self, match):
        url = self.root + "/api/gallery/" + match.group(1)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        self.data = data = util.json_loads(page)

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
        exts = {"j": "jpg", "p": "png", "g": "gif", "w": "webp", "a": "avif"}

        data = self.data
        ufmt = ("https://i{}.nhentai.net/galleries/" +
                data["media_id"] + "/{}.{}").format

        return [
            (ufmt(random.randint(1, 4), num, exts.get(img["t"], "jpg")), {
                "width" : img["w"],
                "height": img["h"],
            })
            for num, img in enumerate(data["images"]["pages"], 1)
        ]


class NhentaiExtractor(Extractor):
    """Base class for nhentai extractors"""
    category = "nhentai"
    root = "https://nhentai.net"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, self.query = match.groups()

    def items(self):
        data = {"_extractor": NhentaiGalleryExtractor}
        for gallery_id in self._pagination():
            url = "{}/g/{}/".format(self.root, gallery_id)
            yield Message.Queue, url, data

    def _pagination(self):
        url = self.root + self.path
        params = text.parse_query(self.query)
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text
            yield from text.extract_iter(page, 'href="/g/', '/')
            if 'class="next"' not in page:
                return
            params["page"] += 1


class NhentaiTagExtractor(NhentaiExtractor):
    """Extractor for nhentai tag searches"""
    subcategory = "tag"
    pattern = (r"(?:https?://)?nhentai\.net("
               r"/(?:artist|category|character|group|language|parody|tag)"
               r"/[^/?#]+(?:/popular[^/?#]*)?/?)(?:\?([^#]+))?")
    example = "https://nhentai.net/tag/TAG/"


class NhentaiSearchExtractor(NhentaiExtractor):
    """Extractor for nhentai search results"""
    subcategory = "search"
    pattern = r"(?:https?://)?nhentai\.net(/search/?)\?([^#]+)"
    example = "https://nhentai.net/search/?q=QUERY"


class NhentaiFavoriteExtractor(NhentaiExtractor):
    """Extractor for nhentai favorites"""
    subcategory = "favorite"
    pattern = r"(?:https?://)?nhentai\.net(/favorites/?)(?:\?([^#]+))?"
    example = "https://nhentai.net/favorites/"
