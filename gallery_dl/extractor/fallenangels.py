# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://www.fascans.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util
import re
import json


class FallenangelsChapterExtractor(Extractor):
    """Extractor for manga-chapters from fascans.com"""
    category = "fallenangels"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{chapter:>03} - {title}"]
    filename_fmt = "{manga}_{chapter:>03}_{page:>03}.{extension}"
    pattern = [(r"(?:https?://)?(manga|truyen)\.fascans\.com/"
                r"manga/([^/]+)/(\d+)")]
    test = [
        ("https://manga.fascans.com/manga/chronos-ruler/20/1", {
            "url": "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
            "keyword": "b2b9c7fd4696b9369d230c3069b5333b476f35d6",
        }),
        ("http://truyen.fascans.com/manga/hungry-marie/8", {
            "url": "1f923d9cb337d5e7bbf4323719881794a951c6ae",
            "keyword": "5520691dbaa26248bcd994e6c6a87bb39710f6c3",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.version, self.manga, self.chapter = match.groups()

    def items(self):
        url = "https://{}.fascans.com/manga/{}/{}/1".format(
            self.version, self.manga, self.chapter)
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
        lang = "vi" if self.version == "truyen" else "en"
        data = {
            "chapter": self.chapter,
            "lang": lang,
            "language": util.code_to_language(lang),
        }
        return text.extract_all(page, (
            ("manga", 'name="description" content="', ' Chapter '),
            ("title", ':  ', ' - Page 1'),
        ), values=data)[0]

    @staticmethod
    def get_images(page):
        """Return a list of all images in this chapter"""
        return json.loads(text.extract(page, "var pages = ", ";")[0])


class FallenangelsMangaExtractor(MangaExtractor):
    """Extractor for manga from fascans.com"""
    category = "fallenangels"
    pattern = [r"(?:https?://)?((manga|truyen)\.fascans\.com/manga/[^/]+)/?$"]
    scheme = "https"
    test = [
        ("http://manga.fascans.com/manga/trinity-seven", {
            "url": "8da3d4bcbadc173e5b23c141a0e646b35f41b9b0",
        }),
        ("https://truyen.fascans.com/manga/rakudai-kishi-no-eiyuutan", {
            "url": "51a731a6b82d5eb7a335fbae6b02d06aeb2ab07b",
        }),
    ]

    def chapters(self, page):
        pattern = r'<h3 class="chapter-title-rtl">\s+<a href="([^"]+)"'
        return re.findall(pattern, page)
