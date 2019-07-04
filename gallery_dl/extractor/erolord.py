# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://erolord.com/"""

from .common import GalleryExtractor
from .. import text, util
import json


class ErolordGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from erolord.com"""
    category = "erolord"
    root = "http://erolord.com"
    pattern = r"(?:https?://)?(?:www\.)?erolord.com(/doujin/(\d+)/?)"
    test = ("http://erolord.com/doujin/2189055/", {
        "url": "7ce6d10a3934102b95c9718a34ccd3d35f55d85f",
        "keyword": {
            "title"     : "Amazon No Hiyaku | Amazon Elixir",
            "gallery_id": 2189055,
            "count"     : 16,
            "artist"    : ["Morris"],
            "group"     : list,
            "parody"    : list,
            "characters": list,
            "tags"      : list,
            "lang"      : "en",
            "language"  : "English",
        },
    })

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def metadata(self, page):
        extr = text.extract_from(page)
        split = text.split_html
        title, _, language = extr('<h1 class="t64">', '</h1>').rpartition(" ")
        language = language.strip("[]")

        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(title),
            # double quotes for anime, circle, tags
            # single quotes for characters, artist
            "parody"    : split(extr('class="sp1">Anime:'     , "</div>\r")),
            "characters": split(extr("class='sp1'>Characters:", "</div>\r")),
            "artist"    : split(extr("class='sp1'>Artist:"    , "</div>\r")),
            "group"     : split(extr('class="sp1">Circle:'    , "</div>\r")),
            "tags"      : split(extr('class="sp1">Tags:'      , "</div>\r")),
            "lang"      : util.language_to_code(language),
            "language"  : language,
        }

    def images(self, page):
        url = self.root + text.extract(page, 'id="d1"><a href="', '"')[0]
        imgs = text.extract(self.request(url).text, 'var imgs=', ';')[0]
        return [(self.root + path, None) for path in json.loads(imgs)]
