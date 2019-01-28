# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://hentaifox.com/"""

from .common import ChapterExtractor
from .. import text


class HentaifoxChapterExtractor(ChapterExtractor):
    """Extractor for a single manga chapter from hentaifox.com"""
    category = "hentaifox"
    filename_fmt = "{category}_{chapter_id}_{page:>03}.{extension}"
    directory_fmt = ["{category}", "{chapter_id} {title}"]
    archive_fmt = "{chapter_id}_{page}"
    pattern = [r"(?:https?://)?(?:www\.)?hentaifox\.com/gallery/(\d+)"]
    test = [("https://hentaifox.com/gallery/56622/", {
        "pattern": r"https://i\d*\.hentaifox\.com/\d+/\d+/\d+\.jpg",
        "count": 24,
        "keyword": "a5cfc962e2b2c929942c357bd67f0cc32f834cec",
    })]
    root = "https://hentaifox.com"

    def __init__(self, match):
        self.chapter_id = match.group(1)
        url = "{}/gallery/{}".format(self.root, self.chapter_id)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        title, pos = text.extract(page, "<h1>", "</h1>")
        data = text.extract_all(page, (
            ("parodies"  , ">Parodies:"  , "</a></span>"),
            ("characters", ">Characters:", "</a></span>"),
            ("tags"      , ">Tags:"      , "</a></span>"),
            ("artist"    , ">Artists:"   , "</a></span>"),
            ("group"     , ">Groups:"    , "</a></span>"),
            ("type"      , ">Category:"  , "</a></span>"),
        ), pos)[0]

        for key, value in data.items():
            data[key] = text.remove_html(value).replace(" , ", ", ")
        data["title"] = text.unescape(title)
        data["chapter_id"] = text.parse_int(self.chapter_id)
        data["language"] = "English"
        data["lang"] = "en"

        return data

    def get_images(self, page):
        return [
            (text.urljoin(self.root, url.replace("t.", ".")), None)
            for url in text.extract_iter(page, 'data-src="', '"')
        ]
