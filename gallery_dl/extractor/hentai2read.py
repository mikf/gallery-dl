# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://hentai2read.com/"""

from .common import Extractor, Message
from .. import text
import json
import re

class Hentai2readMangaExtractor(Extractor):
    """Extractor for mangas from hentai2read.com"""
    category = "hentai2read"
    subcategory = "manga"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/?$"]
    test = [
        ("http://hentai2read.com/amazon_elixir/", {
            "url": "d1f87b71d3c97b49a478cdfb6ae96b2d9520ab78",
        }),
        ("http://hentai2read.com/oshikage_riot/", {
            "url": "672f34cce7bf5a855c6c38e8bc9c5117a4b3061c",
        })
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title = match.group(1)

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request("http://hentai2read.com/" + self.url_title).text
        page = text.extract(page, '<ul class="nav-chapters remove-margin-b">', '</ul>\n</div>')[0]
        needle = '<li>\n<a href="'
        return reversed(list(
            text.extract_iter(page, needle, '"')
        ))

class Hentai2readChapterExtractor(Extractor):
    """Extractor for a single manga chapter from hentai2read.com"""
    category = "hentai2read"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{gallery-id} {title}"]
    filename_fmt = "{category}_{gallery-id}_{chapter:>02}_{num:>03}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?hentai2read\.com/([^/]+)/(\d+)"]
    test = [("http://hentai2read.com/amazon_elixir/1/", {
        "url": "fb5fc4d7cc194116960eaa648c7e045a6e6f0c11",
        "keyword": "03435037539d57ca084c457b5ac4d48928487521",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url_title, self.chapter = match.groups()

    def items(self):
        url = "http://hentai2read.com/{}/{}/".format(self.url_title, self.chapter)
        page = self.request(url).text
        images = self.get_image_urls(page)
        data = self.get_job_metadata(page, images)
        yield Message.Version, 1
        yield Message.Directory, data
        for num, part in enumerate(images, 1):
            data["num"] = num
            url = "http://hentaicdn.com/hentai" + part
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page, images):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0]
        match = re.match(r"Reading (?:(.+) dj - )?(.+) Hentai - \d+: ", title)
        return {
            "gallery-id": images[0].split("/")[-3],
            "chapter": self.chapter,
            "count": len(images),
            "series": match.group(1) or "",
            "title": match.group(2),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        images = text.extract(page, "var rff_imageList = ", ";")[0]
        return json.loads(images)
