# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://www.fascans.com/"""

from .common import Extractor, MangaExtractor, Message
from .. import text, util
import json


class FallenangelsChapterExtractor(Extractor):
    """Extractor for manga-chapters from fascans.com"""
    category = "fallenangels"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}",
                     "c{chapter:>03}{chapter_minor}{title:?: //}"]
    filename_fmt = (
        "{manga}_c{chapter:>03}{chapter_minor}_{page:>03}.{extension}")
    pattern = [(r"(?:https?://)?(manga|truyen)\.fascans\.com/"
                r"manga/([^/]+)/(\d+)(\.[^/?&#]+)?")]
    test = [
        ("https://manga.fascans.com/manga/chronos-ruler/20/1", {
            "url": "4604a7914566cc2da0ff789aa178e2d1c8c241e3",
            "keyword": "4e1722cf0ed8ee5fc5c64147ac3f39342e767cd8",
        }),
        ("http://truyen.fascans.com/manga/hungry-marie/8", {
            "url": "1f923d9cb337d5e7bbf4323719881794a951c6ae",
            "keyword": "c7beeb7d8a65d5d8ab451f076f584bd4d52b7210",
        }),
        ("http://manga.fascans.com/manga/rakudai-kishi-no-eiyuutan/19.5", {
            "keyword": "bf7dd1c462a80ffe50b92fec00b7acda2f8b800e",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.version, self.manga, self.chapter, self.minor = match.groups()

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
            "chapter_minor": self.minor or "",
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
            "url": "b4904e25f023cff7174dd3f73000db4d4e81a4e2",
            "keyword": "042eabfa6067fde9e3502edb7e9c8df2dbed8ac6",
        }),
        ("https://truyen.fascans.com/manga/rakudai-kishi-no-eiyuutan", {
            "url": "51a731a6b82d5eb7a335fbae6b02d06aeb2ab07b",
            "keyword": "2d2a2a5d9ea5925eb9a47bb13d848967f3af086c",
        }),
    ]

    def __init__(self, match):
        MangaExtractor.__init__(self, match)
        self.lang = "vi" if match.group(2) == "truyen" else "en"

    def chapters(self, page):
        language = util.code_to_language(self.lang)
        results = []
        pos = 0
        while True:
            test, pos = text.extract(page, '<li style="', '', pos)
            if test is None:
                return results
            volume , pos = text.extract(page, 'class="volume-', '"', pos)
            url    , pos = text.extract(page, 'href="', '"', pos)
            chapter, pos = text.extract(page, '>', '<', pos)
            title  , pos = text.extract(page, '<em>', '</em>', pos)

            manga, _, chapter = chapter.rpartition(" ")
            chapter, dot, minor = chapter.partition(".")
            results.append((url, {
                "manga": manga, "title": title,
                "volume": util.safe_int(volume),
                "chapter": util.safe_int(chapter),
                "chapter_minor": dot + minor,
                "lang": self.lang, "language": language,
            }))
