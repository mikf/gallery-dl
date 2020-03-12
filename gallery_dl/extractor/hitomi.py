# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hitomi.la/"""

from .common import GalleryExtractor
from .. import text, util
import string
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
            "keyword": "6701f8f588f119ef84cd29bdf99a399417b0a6a2",
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
        self.info = None
        self.session.headers["Referer"] = "{}/reader/{}.html".format(
            self.root, gid)

    def metadata(self, page):
        self.info = info = json.loads(page.partition("=")[2])

        data = self._data_from_gallery_info(info)
        if self.config("metadata", True):
            data.update(self._data_from_gallery_page(info))
        return data

    def _data_from_gallery_info(self, info):
        language = info.get("language")
        if language:
            language = language.capitalize()

        tags = []
        for tinfo in info["tags"]:
            tag = tinfo["tag"]
            if tinfo.get("female"):
                tag += " ♀"
            elif tinfo.get("male"):
                tag += " ♂"
            tags.append(string.capwords(tag))

        return {
            "gallery_id": text.parse_int(info["id"]),
            "title"     : info["title"],
            "type"      : info["type"].capitalize(),
            "language"  : language,
            "lang"      : util.language_to_code(language),
            "tags"      : tags,
            "date"      : text.parse_datetime(
                info["date"] + ":00", "%Y-%m-%d %H:%M:%S%z"),
        }

    def _data_from_gallery_page(self, info):
        url = "{}/galleries/{}.html".format(self.root, info["id"])

        # follow redirects
        while True:
            response = self.request(url, fatal=False)
            if b"<title>Redirect</title>" not in response.content:
                break
            url = text.extract(response.text, "href='", "'")[0]
            if not url.startswith("http"):
                url = text.urljoin(self.root, url)

        if response.status_code >= 400:
            return {}

        def prep(value):
            return [
                text.unescape(string.capwords(v))
                for v in text.extract_iter(value or "", '.html">', '<')
            ]

        extr = text.extract_from(response.text)
        return {
            "artist"    : prep(extr('<h2>', '</h2>')),
            "group"     : prep(extr('<td>Group</td><td>', '</td>')),
            "parody"    : prep(extr('<td>Series</td><td>', '</td>')),
            "characters": prep(extr('<td>Characters</td><td>', '</td>')),
        }

    def images(self, _):
        result = []
        for image in self.info["files"]:
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
