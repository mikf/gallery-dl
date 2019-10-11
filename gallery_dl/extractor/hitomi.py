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
            "pattern": r"https://aa.hitomi.la/galleries/867789/\d+.jpg",
            "keyword": "d097a8db8e810045131b4510c41714004f9eff3a",
            "count": 16,
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
        ("https://hitomi.la/galleries/1045954.html", {
            # fallback for galleries only available through /reader/ URLs
            "url": "055c898a36389719799d6bce76889cc4ea4421fc",
            "count": 1413,
        }),
        ("https://hitomi.la/reader/867789.html"),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        self.fallback = False
        url = "{}/galleries/{}.html".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def request(self, url, **kwargs):
        response = GalleryExtractor.request(self, url, fatal=False, **kwargs)
        if response.status_code == 404:
            self.fallback = True
            url = url.replace("/galleries/", "/reader/")
            response = GalleryExtractor.request(self, url, **kwargs)
        return response

    def metadata(self, page):
        if self.fallback:
            return {
                "gallery_id": text.parse_int(self.gallery_id),
                "title": text.unescape(text.extract(
                    page, "<title>", "<")[0].rpartition(" | ")[0]),
            }

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
        # see https://ltn.hitomi.la/common.js
        offset = text.parse_int(self.gallery_id[-1]) % 3
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
        elif self.fallback:
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
