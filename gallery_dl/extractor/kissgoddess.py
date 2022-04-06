# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kissgoddess.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, exception


class KissgoddessGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries on kissgoddess.com"""
    category = "kissgoddess"
    root = "https://kissgoddess.com"
    pattern = r"(?:https?://)?(?:www\.)?kissgoddess\.com/album/(\d+)"
    test = ("https://kissgoddess.com/album/18285.html", {
        "pattern": r"https://pic\.kissgoddess\.com"
                   r"/gallery/16473/18285/s/\d+\.jpg",
        "count": 19,
        "keyword": {
            "gallery_id": 18285,
            "title": "[Young Champion Extra] 2016.02 No.03 菜乃花 安枝瞳 葉月あや",
        },
    })

    def __init__(self, match):
        self.gallery_id = match.group(1)
        url = "{}/album/{}.html".format(self.root, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.extract(
                page, '<title>', "<")[0].rpartition(" | ")[0],
        }

    def images(self, page):
        pnum = 1

        while page:
            for url in text.extract_iter(page, "<img src='", "'"):
                yield url, None
            for url in text.extract_iter(page, "<img data-original='", "'"):
                yield url, None

            pnum += 1
            url = "{}/album/{}_{}.html".format(
                self.root, self.gallery_id, pnum)
            try:
                page = self.request(url).text
            except exception.HttpError:
                return


class KissgoddessModelExtractor(Extractor):
    """Extractor for all galleries of a model on kissgoddess.com"""
    category = "kissgoddess"
    subcategory = "model"
    root = "https://kissgoddess.com"
    pattern = r"(?:https?://)?(?:www\.)?kissgoddess\.com/people/([^./?#]+)"
    test = ("https://kissgoddess.com/people/aya-hazuki.html", {
        "pattern": KissgoddessGalleryExtractor.pattern,
        "count": ">= 7",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.model = match.group(1)

    def items(self):
        url = "{}/people/{}.html".format(self.root, self.model)
        page = self.request(url).text

        data = {"_extractor": KissgoddessGalleryExtractor}
        for path in text.extract_iter(page, 'thumb"><a href="/album/', '"'):
            url = self.root + "/album/" + path
            yield Message.Queue, url, data
