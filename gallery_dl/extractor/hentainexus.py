# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentainexus.com/"""

from .common import GalleryExtractor
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
            "url": "57238d6e76a199298c9866bbcfaa111c0fa164b0",
            "keyword": "5b254937a180b5c2cef303324cd5f7f6fec98d55",
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
        imgs = extr("initReader(", "]") + "]"
        base = extr('"', '"')

        return [(base + img, None) for img in json.loads(imgs)]
