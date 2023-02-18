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

    def __init__(self, match):
        super().__init__(match)
        self.item = match.group(1)
        self.session.headers["Referer"] = self.root

    def items(self):
        for gallery in self.galleries():
            gallery["_extractor"] = PornpicsGalleryExtractor
            yield Message.Queue, gallery["g_url"], gallery

    def _pagination(self, url, params=None):
        if params is None:
            # fetch first 20 galleries from HTML
            # since '"offset": 0' does not return a JSON response
            page = self.request(url).text
            for path in text.extract_iter(
                    page, 'class="rel-link" href="', '"'):
                yield {"g_url": self.root + path}
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
    pattern = BASE_PATTERN + r"(/galleries/(?:[^/?#]+-)?(\d+))"
    test = (
        (("https://www.pornpics.com/galleries/british-beauty-danielle-flashes-"
          "hot-breasts-ass-and-snatch-in-the-forest-62610699/"), {
            "pattern": r"https://cdni\.pornpics\.com/1280/7/160/62610699"
                       r"/62610699_\d+_[0-9a-f]{4}\.jpg",
            "keyword": {
                "categories": ["MILF", "Amateur", "Sexy", "Outdoor"],
                "channel": "FTV MILFs",
                "count": 17,
                "gallery_id": 62610699,
                "models": ["Danielle"],
                "num": int,
                "slug": "british-beauty-danielle-flashes-"
                        "hot-breasts-ass-and-snatch-in-the-forest",
                "tags": ["Amateur MILF", "Sexy MILF"],
                "title": "British beauty Danielle flashes "
                         "hot breasts, ass and snatch in the forest",
                "views": int,
            },
        }),
        ("https://pornpics.com/es/galleries/62610699", {
            "keyword": {
                "slug": "british-beauty-danielle-flashes-"
                        "hot-breasts-ass-and-snatch-in-the-forest",
            },
        }),
    )

    def __init__(self, match):
        PornpicsExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    items = GalleryExtractor.items

    def metadata(self, page):
        extr = text.extract_from(page)

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "slug"      : extr("/galleries/", "/").rpartition("-")[0],
            "title"     : text.unescape(extr("<h1>", "<")),
            "channel"   : extr('>Channel:', '</a>').rpartition(">")[2],
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
    test = (
        ("https://www.pornpics.com/tags/summer-dress/", {
            "pattern": PornpicsGalleryExtractor.pattern,
            "range": "1-50",
            "count": 50,
        }),
        ("https://pornpics.com/fr/tags/summer-dress"),
    )

    def galleries(self):
        url = "{}/tags/{}/".format(self.root, self.item)
        return self._pagination(url)


class PornpicsSearchExtractor(PornpicsExtractor):
    """Extractor for galleries from pornpics search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:\?q=|pornstars/|channels/)([^/&#]+)"
    test = (
        ("https://www.pornpics.com/?q=nature", {
            "pattern": PornpicsGalleryExtractor.pattern,
            "range": "1-50",
            "count": 50,
        }),
        ("https://www.pornpics.com/channels/femjoy/", {
            "pattern": PornpicsGalleryExtractor.pattern,
            "range": "1-50",
            "count": 50,
        }),
        ("https://www.pornpics.com/pornstars/emma-brown/", {
            "pattern": PornpicsGalleryExtractor.pattern,
            "range": "1-50",
            "count": 50,
        }),
        ("https://pornpics.com/jp/?q=nature"),
        ("https://pornpics.com/it/channels/femjoy"),
        ("https://pornpics.com/pt/pornstars/emma-brown"),
    )

    def galleries(self):
        url = self.root + "/search/srch.php"
        params = {
            "q"     : self.item.replace("-", " "),
            "lang"  : "en",
            "offset": 0,
        }
        return self._pagination(url, params)
