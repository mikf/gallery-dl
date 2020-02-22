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
        self.gallery_id = match.group(1)
        url = "https://ltn.hitomi.la/galleries/{}.js".format(self.gallery_id)
        GalleryExtractor.__init__(self, match, url)
        self.session.headers["Referer"] = "{}/reader/{}.html".format(
            self.root, self.gallery_id)

    def metadata(self, _):
        # try galleries page first
        url = "{}/galleries/{}.html".format(self.root, self.gallery_id)
        response = self.request(url, fatal=False)

        # follow redirects
        while b"<title>Redirect</title>" in response.content:
            url = text.extract(response.text, "href='", "'")[0]
            if not url.startswith("http"):
                url = text.urljoin(self.root, url)
            response = self.request(url, fatal=False)

        # fallback to reader page
        if response.status_code >= 400:
            url = "{}/reader/{}.html".format(self.root, self.gallery_id)
            page = self.request(url).text
            return {
                "gallery_id": text.parse_int(self.gallery_id),
                "title": text.unescape(text.extract(
                    page, "<title>", "<")[0].rpartition(" | ")[0]),
            }

        page = response.text
        extr = text.extract_from(page, page.index('<h1><a href="/reader/'))
        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(extr('.html">', '<').strip()),
            "artist"    : self._prep(extr('<h2>', '</h2>')),
            "group"     : self._prep(extr('<td>Group</td><td>', '</td>')),
            "type"      : self._prep_1(extr('<td>Type</td><td>', '</td>')),
            "language"  : self._prep_1(extr('<td>Language</td><td>', '</td>')),
            "parody"    : self._prep(extr('<td>Series</td><td>', '</td>')),
            "characters": self._prep(extr('<td>Characters</td><td>', '</td>')),
            "tags"      : self._prep(extr('<td>Tags</td><td>', '</td>')),
            "date"      : self._date(extr('<span class="date">', '</span>')),
        }
        if data["language"] == "N/a":
            data["language"] = None
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, page):
        result = []
        for image in json.loads(page.partition("=")[2])["files"]:
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

    @staticmethod
    def _prep(value):
        return [
            text.unescape(string.capwords(v))
            for v in text.extract_iter(value or "", '.html">', '<')
        ]

    @staticmethod
    def _prep_1(value):
        return text.remove_html(value).capitalize()

    @staticmethod
    def _date(value):
        return text.parse_datetime(value + ":00", "%Y-%m-%d %H:%M:%S%z")
