# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://fascans.com/"""

from .common import Extractor, Message
from .. import text
import json


class FallenangelsChapterExtractor(Extractor):
    """Extractor for manga-chapters from fascans.com"""
    category = "fallenangels"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter:>03} - {title}"]
    filename_fmt = "{manga}_{chapter:>03}_{page:>03}.{extension}"
    pattern = [r"(?:https?://)?manga\.fascans\.com/manga/([^/]+)/(\d+)"]
    test = [("https://manga.fascans.com/manga/chronos-ruler/20/1", {
        "url": "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
        "keyword": "b2b9c7fd4696b9369d230c3069b5333b476f35d6",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.manga, self.chapter = match.groups()

    def items(self):
        url = "https://manga.fascans.com/manga/{}/{}/1".format(
            self.manga, self.chapter)
        page = self.request(url).text
        data = self.get_metadata(page)
        imgs = self.get_images(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], img in enumerate(imgs, 1):
            url = img["page_image"]
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "chapter": self.chapter,
            "lang": "en",
            "language": "English",
        }
        return text.extract_all(page, (
            ("manga", 'name="description" content="', ' Chapter '),
            ("title", ':  ', ' - Page 1'),
        ), values=data)[0]

    @staticmethod
    def get_images(page):
        """Return a list of all images in this chapter"""
        return json.loads(text.extract(page, "var pages = ", ";")[0])
