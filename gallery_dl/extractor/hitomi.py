# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hitomi.la/"""

from .common import GalleryExtractor
from .. import text, util
import json


class HitomiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    root = "https://hitomi.la"
    pattern = (r"(?:https?://)?hitomi\.la"
               r"/(?:manga|doujinshi|cg|gamecg|galleries|reader)"
               r"/(?:[^/?&#]+-)?(\d+)")
    test = (
        ("https://hitomi.la/galleries/867789.html", {
            "pattern": r"https://[a-c]a.hitomi.la/images/./../[0-9a-f]+.jpg",
            "keyword": "3314105a0b344ea1461c43257b14b0de415b88bb",
            "count": 16,
        }),
        # download test
        ("https://hitomi.la/galleries/1401410.html", {
            "range": "1",
            "content": "b3ca8c6c8cc5826cf8b4ceb7252943abad7b8b4c",
        }),
        # Game CG with scenes (#321)
        ("https://hitomi.la/galleries/733697.html", {
            "url": "b4cbc76032852db4a655bf6a2c4d58eae8153c8e",
            "count": 210,
        }),
        # fallback for galleries only available through /reader/ URLs
        ("https://hitomi.la/galleries/1045954.html", {
            "url": "f3aa914ad148437f72d307268fa0d250eabe8dab",
            "count": 1413,
        }),
        # gallery with "broken" redirect
        ("https://hitomi.la/cg/scathacha-sama-okuchi-ecchi-1291900.html", {
            "count": 10,
        }),
        ("https://hitomi.la/manga/amazon-no-hiyaku-867789.html"),
        ("https://hitomi.la/manga/867789.html"),
        ("https://hitomi.la/doujinshi/867789.html"),
        ("https://hitomi.la/cg/867789.html"),
        ("https://hitomi.la/gamecg/867789.html"),
        ("https://hitomi.la/reader/867789.html"),
    )

    def __init__(self, match):
        gid = match.group(1)
        url = "https://ltn.hitomi.la/galleries/{}.js".format(gid)
        GalleryExtractor.__init__(self, match, url)
        self.data = None
        self.session.headers["Referer"] = "{}/reader/{}.html".format(
            self.root, gid)

    def metadata(self, page):
        self.data = data = json.loads(page.partition("=")[2])

        language = data.get("language")
        if language:
            language = language.capitalize()

        tags = []
        for tinfo in data["tags"]:
            tag = tinfo["tag"]
            if tinfo.get("female"):
                tag = "female:" + tag
            elif tinfo.get("male"):
                tag = "male:" + tag
            tags.append(tag)

        return {
            "gallery_id": text.parse_int(data["id"]),
            "title"     : data["title"],
            "type"      : data["type"],
            "language"  : language,
            "lang"      : util.language_to_code(language),
            "tags"      : tags,
            "date"      : text.parse_datetime(
                data["date"] + ":00", "%Y-%m-%d %H:%M:%S%z"),
        }

    def images(self, _):
        result = []
        for image in self.data["files"]:
            ihash = image["hash"]
            idata = text.nameext_from_url(image["name"])

            # see https://ltn.hitomi.la/common.js
            inum = int(ihash[-3:-1], 16)
            frontends = 2 if inum < 0x30 else 3
            inum = 1 if inum < 0x09 else inum

            url = "https://{}a.hitomi.la/images/{}/{}/{}.{}".format(
                chr(97 + (inum % frontends)),
                ihash[-1], ihash[-3:-1], ihash,
                idata["extension"],
            )
            result.append((url, idata))
        return result
