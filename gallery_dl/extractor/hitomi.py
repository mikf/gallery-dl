# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hitomi.la/"""

from .common import GalleryExtractor
from .. import text, util
import string


class HitomiGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from hitomi.la"""
    category = "hitomi"
    root = "https://hitomi.la"
    pattern = r"(?:https?://)?hitomi\.la/(?:galleries|reader)/(\d+)"
    test = (
        ("https://hitomi.la/galleries/867789.html", {
            "url": "cb759868d090fe0e2655c3e29ebf146054322b6d",
            "keyword": "d097a8db8e810045131b4510c41714004f9eff3a",
        }),
        ("https://hitomi.la/galleries/1036181.html", {
            # "aa" subdomain for gallery-id ending in 1 (#142)
            "pattern": r"https://aa\.hitomi\.la/",
        }),
        ("https://hitomi.la/galleries/1401410.html", {
            # download test
            "range": "1",
            "content": "b3ca8c6c8cc5826cf8b4ceb7252943abad7b8b4c",
        }),
        ("https://hitomi.la/galleries/733697.html", {
            # Game CG with scenes (#321)
            "url": "c2a84185f467450b8b9b72fbe40c0649029ce007",
            "count": 210,
        }),
        ("https://hitomi.la/reader/867789.html"),
    )

    def __init__(self, match):
        self.gallery_id = text.parse_int(match.group(1))
        url = "{}/galleries/{}.html".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page, page.index('<h1><a href="/reader/'))
        data = {
            "gallery_id": self.gallery_id,
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
        # see https://ltn.hitomi.la/common.js
        offset = self.gallery_id % 2 if self.gallery_id % 10 != 1 else 0
        subdomain = chr(97 + offset) + "a"
        base = "https://" + subdomain + ".hitomi.la/galleries/"

        # set Referer header before image downloads (#239)
        self.session.headers["Referer"] = self.chapter_url

        # handle Game CG galleries with scenes (#321)
        scenes = text.extract(page, "var scene_indexes = [", "]")[0]
        if scenes and scenes.strip():
            url = "{}/reader/{}.html".format(self.root, self.gallery_id)
            page = self.request(url).text
            begin, end = ">//g.hitomi.la/galleries/", "</div>"
        else:
            begin, end = "'//tn.hitomi.la/smalltn/", ".jpg',"

        return [
            (base + urlpart, None)
            for urlpart in text.extract_iter(page, begin, end)
        ]

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
