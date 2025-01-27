# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pornpics.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pornpics\.com(?:/\w\w)?"


class PornpicsExtractor(Extractor):
    """Base class for pornpics extractors"""
    category = "pornpics"
    root = "https://www.pornpics.com"
    request_interval = (0.5, 1.5)

    def items(self):
        for gallery in self.galleries():
            gallery["_extractor"] = PornpicsGalleryExtractor
            yield Message.Queue, gallery["g_url"], gallery

    def _pagination(self, url, params=None):
        if params is None:
            # fetch first 20 galleries from HTML
            # since '"offset": 0' does not return a JSON response
            page = self.request(url).text
            for href in text.extract_iter(
                    page, 'class="rel-link" href="', '"'):
                if href[0] == "/":
                    href = self.root + href
                yield {"g_url": href}
            del page
            params = {"offset": 20}

        limit = params["limit"] = 20

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": url if params["offset"] else self.root + "/",
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            galleries = self.request(
                url, params=params, headers=headers).json()
            yield from galleries

            if len(galleries) < limit:
                return
            params["offset"] += limit


class PornpicsGalleryExtractor(PornpicsExtractor, GalleryExtractor):
    """Extractor for pornpics galleries"""
    pattern = BASE_PATTERN + r"/galleries/((?:[^/?#]+-)?(\d+))"
    example = "https://www.pornpics.com/galleries/TITLE-12345/"

    def __init__(self, match):
        url = "{}/galleries/{}/".format(self.root, match.group(1))
        GalleryExtractor.__init__(self, match, url)

    items = GalleryExtractor.items

    def metadata(self, page):
        extr = text.extract_from(page)

        return {
            "gallery_id": text.parse_int(self.groups[1]),
            "slug"      : extr("/galleries/", "/").rpartition("-")[0],
            "title"     : text.unescape(extr("<h1>", "<")),
            "channel"   : text.split_html(extr(">Channel:&nbsp;", '</div>')),
            "models"    : text.split_html(extr(
                ">Models:", '<span class="suggest')),
            "categories": text.split_html(extr(
                ">Categories:", '<span class="suggest')),
            "tags"      : text.split_html(extr(
                ">Tags List:", ' </div>')),
            "views"    : text.parse_int(extr(">Views:", "<").replace(",", "")),
        }

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(page, "class='rel-link' href='", "'")
        ]


class PornpicsTagExtractor(PornpicsExtractor):
    """Extractor for galleries from pornpics tag searches"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tags/([^/?#]+)"
    example = "https://www.pornpics.com/tags/TAGS/"

    def galleries(self):
        url = "{}/tags/{}/".format(self.root, self.groups[0])
        return self._pagination(url)


class PornpicsSearchExtractor(PornpicsExtractor):
    """Extractor for galleries from pornpics search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:\?q=|pornstars/|channels/)([^/&#]+)"
    example = "https://www.pornpics.com/?q=QUERY"

    def galleries(self):
        url = self.root + "/search/srch.php"
        params = {
            "q"     : self.groups[0].replace("-", " "),
            "lang"  : "en",
            "offset": 0,
        }
        return self._pagination(url, params)
