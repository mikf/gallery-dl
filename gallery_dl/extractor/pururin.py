# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pururin.to/"""

from .common import GalleryExtractor
from .. import text, util


class PururinGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on pururin.io"""
    category = "pururin"
    root = "https://pururin.to"
    pattern = r"(?:https?://)?(?:www\.)?pururin\.[ti]o/(?:gallery|read)/(\d+)"
    example = "https://pururin.to/gallery/12345/TITLE"

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/gallery/{}/x".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)

        def _lst(e=extr):
            v = text.unescape(e('value="', '"'))
            return [item["name"] for item in util.json_loads(v)] if v else ()

        def _str(key, e=extr):
            return text.unescape(text.extr(
                e(key, "</td>"), 'title="', '"')).partition(" / ")[0]

        title = text.unescape(extr('<h1><span itemprop="name">', '<'))
        title_en, _, title_ja = title.partition(" / ")

        data = {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : title_en or title_ja,
            "title_en"  : title_en,
            "title_ja"  : title_ja,
            "language"  : _str("<td>Language</td>"),
            "type"      : _str("<td>Category</td>"),
            "uploader"  : text.remove_html(extr("<td>Uploader</td>", "</td>")),
            "rating"    : text.parse_float(extr(
                'itemprop="ratingValue" content="', '"')),
            "artist"    : extr('name="artist_tags"', '') or _lst(),
            "group"     : _lst(),
            "parody"    : _lst(),
            "tags"      : _lst(),
            "characters": _lst(),
            "scanlator" : _lst(),
            "convention": _lst(),
            "collection": _lst(),
        }
        data["lang"] = util.language_to_code(data["language"])
        return data

    def images(self, _):
        url = "{}/read/{}/01/x".format(self.root, self.gallery_id)
        page = self.request(url).text

        svr, pos = text.extract(page, 'data-svr="', '"')
        img, pos = text.extract(page, 'data-img="', '"', pos)
        data = util.json_loads(text.unescape(img))

        base = "{}/{}/".format(svr, data["directory"])
        return [(base + i["filename"], None) for i in data["images"]]
