# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters and entire manga from http://kissmanga.com/"""

from .common import Extractor, Message
from .. import text, cloudflare
import re


class KissmangaExtractor(Extractor):
    """Base class for kissmanga extractors"""
    category = "kissmanga"
    directory_fmt = ["{category}", "{manga}",
                     "c{chapter:>03}{chapter-minor} - {title}"]
    filename_fmt = ("{manga}_c{chapter:>03}{chapter-minor}_"
                    "{page:>03}.{extension}")
    root = "http://kissmanga.com"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.session.headers["Referer"] = self.root

    request = cloudflare.request_func


class KissmangaMangaExtractor(KissmangaExtractor):
    """Extractor for mangas from kissmanga.com"""
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?kissmanga\.com/Manga/[^/]+/?$"]
    test = [("http://kissmanga.com/Manga/Dropout", {
        "url": "992befdd64e178fe5af67de53f8b510860d968ca",
    })]

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.root + chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        return reversed(list(
            text.extract_iter(page, '<td>\n<a href="', '"')
        ))


class KissmangaChapterExtractor(KissmangaExtractor):
    """Extractor for manga-chapters from kissmanga.com"""
    subcategory = "chapter"
    pattern = [r"(?:https?://)?(?:www\.)?kissmanga\.com/Manga/.+/.+\?id=\d+"]
    test = [
        ("http://kissmanga.com/Manga/Dropout/Ch-000---Oneshot-?id=145847", {
            "url": "4136bcd1c6cecbca8cc2bc965d54f33ef0a97cc0",
            "keyword": "ab332093a4f2e473a468235bfd624cbe3b19fd7f",
        }),
        ("http://kissmanga.com/Manga/Urban-Tales/a?id=256717", {
            "url": "de074848f6c1245204bb9214c12bcc3ecfd65019",
            "keyword": "013aad80e578c6ccd2e1fe47cdc27c12a64f6db2",
        })
    ]

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        manga, pos = text.extract(page, "Read manga\n", "\n")
        cinfo, pos = text.extract(page, "", "\n", pos)
        match = re.match((r"(?:Vol.0*(\d+) )?(?:Ch.)?0*(\d+)"
                          r"(?:\.0*(\d+))?(?:: (.+))?"), cinfo)
        chminor = match.group(3)
        return {
            "manga": manga,
            "volume": match.group(1) or "",
            "chapter": match.group(2),
            "chapter-minor": "."+chminor if chminor else "",
            "title": match.group(4) or "",
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract list of all image-urls for a manga chapter"""
        return list(text.extract_iter(page, 'lstImages.push("', '"'))
