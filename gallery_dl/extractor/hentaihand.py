# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaihand.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util


class HentaihandGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on hentaihand.com"""
    category = "hentaihand"
    root = "https://hentaihand.com"
    pattern = r"(?:https?://)?(?:www\.)?hentaihand\.com/\w+/comic/([\w-]+)"
    example = "https://hentaihand.com/en/comic/TITLE"

    def __init__(self, match):
        self.slug = match.group(1)
        url = "{}/api/comics/{}".format(self.root, self.slug)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        info = util.json_loads(page)
        data = {
            "gallery_id" : text.parse_int(info["id"]),
            "title"      : info["title"],
            "title_alt"  : info["alternative_title"],
            "slug"       : self.slug,
            "type"       : info["category"]["name"],
            "language"   : info["language"]["name"],
            "lang"       : util.language_to_code(info["language"]["name"]),
            "tags"       : [t["slug"] for t in info["tags"]],
            "date"       : text.parse_datetime(
                info["uploaded_at"], "%Y-%m-%d"),
        }
        for key in ("artists", "authors", "groups", "characters",
                    "relationships", "parodies"):
            data[key] = [v["name"] for v in info[key]]
        return data

    def images(self, _):
        info = self.request(self.gallery_url + "/images").json()
        return [(img["source_url"], img) for img in info["images"]]


class HentaihandTagExtractor(Extractor):
    """Extractor for tag searches on hentaihand.com"""
    category = "hentaihand"
    subcategory = "tag"
    root = "https://hentaihand.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentaihand\.com"
               r"/\w+/(parody|character|tag|artist|group|language"
               r"|category|relationship)/([^/?#]+)")
    example = "https://hentaihand.com/en/tag/TAG"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.type, self.key = match.groups()

    def items(self):
        if self.type[-1] == "y":
            tpl = self.type[:-1] + "ies"
        else:
            tpl = self.type + "s"

        url = "{}/api/{}/{}".format(self.root, tpl, self.key)
        tid = self.request(url, notfound=self.type).json()["id"]

        url = self.root + "/api/comics"
        params = {
            "per_page": "18",
            tpl       : tid,
            "page"    : 1,
            "q"       : "",
            "sort"    : "uploaded_at",
            "order"   : "desc",
            "duration": "day",
        }
        while True:
            info = self.request(url, params=params).json()

            for gallery in info["data"]:
                gurl = "{}/en/comic/{}".format(self.root, gallery["slug"])
                gallery["_extractor"] = HentaihandGalleryExtractor
                yield Message.Queue, gurl, gallery

            if params["page"] >= info["last_page"]:
                return
            params["page"] += 1
