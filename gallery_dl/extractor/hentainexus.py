# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentainexus.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import json


class HentainexusGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on hentainexus.com"""
    category = "hentainexus"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"/(?:view|read)/(\d+)")
    test = (
        ("https://hentainexus.com/view/5688", {
            "url": "746d0043e20030f1171aae5ea113176607302517",
            "keyword": "b05986369fbaf29cfa08b118960d92c49e59524b",
        }),
        ("https://hentainexus.com/read/5688"),
    )

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/view/{}".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        rmve = text.remove_html
        extr = text.extract_from(page)
        data = {
            "gallery_id" : text.parse_int(self.gallery_id),
            "tags"       : extr('"og:description" content="', '"').split(", "),
            "thumbnail"  : extr('"og:image" content="', '"'),
            "title"      : extr('<h1 class="title">', '</h1>'),
            "artist"     : rmve(extr('viewcolumn">Artist</td>'     , '</td>')),
            "book"       : rmve(extr('viewcolumn">Book</td>'       , '</td>')),
            "language"   : rmve(extr('viewcolumn">Language</td>'   , '</td>')),
            "magazine"   : rmve(extr('viewcolumn">Magazine</td>'   , '</td>')),
            "parody"     : rmve(extr('viewcolumn">Parody</td>'     , '</td>')),
            "publisher"  : rmve(extr('viewcolumn">Publisher</td>'  , '</td>')),
            "description": rmve(extr('viewcolumn">Description</td>', '</td>')),
        }
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, page):
        url = "{}/read/{}".format(self.root, self.gallery_id)
        extr = text.extract_from(self.request(url).text)
        urls = extr("initReader(", "]") + "]"
        return [(url, None) for url in json.loads(urls)]


class HentainexusSearchExtractor(Extractor):
    """Extractor for search results on hentainexus.com"""
    category = "hentainexus"
    subcategory = "search"
    root = "https://hentainexus.com"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?hentainexus\.com"
               r"(?:/page/\d+)?/?(?:\?(q=[^/?#]+))?$")
    test = (
        ("https://hentainexus.com/?q=tag:%22heart+pupils%22%20tag:group", {
            "pattern": HentainexusGalleryExtractor.pattern,
            "count": ">= 50",
        }),
        ("https://hentainexus.com/page/3?q=tag:%22heart+pupils%22"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.params = text.parse_query(match.group(1))

    def items(self):
        yield Message.Version, 1
        params = self.params
        path = "/"

        while path:
            page = self.request(self.root + path, params=params).text
            extr = text.extract_from(page)
            data = {"_extractor": HentainexusGalleryExtractor}

            while True:
                gallery_id = extr('<a href="/view/', '"')
                if not gallery_id:
                    break
                yield Message.Queue, self.root + "/view/" + gallery_id, data

            path = extr('class="pagination-next" href="', '"')
