# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.bobx.com/dark/"""

from .common import Extractor, Message
from .. import text


class BobxExtractor(Extractor):
    """Base class for bobx extractors"""
    category = "bobx"
    root = "http://www.bobx.com"
    per_page = 80

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)


class BobxGalleryExtractor(BobxExtractor):
    """Extractor for individual image galleries on bobx.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{model}", "{title}")
    filename_fmt = "{model}_{image_id}_{num:>03}.{extension}"
    archive_fmt = "{image_id}"
    pattern = (r"(?:https?://)?(?:www\.)?bobx\.com"
               r"/([^/]+/[^/]+/photoset/[\w-]+)-\d+-\d+-\d+\.html")
    test = (
        (("http://www.bobx.com/idol/mikoto-hibi"
          "/photoset/wpb-2018-_11-0-2-8.html"), {
            "url": "93972d6a661f6627e963d62c9d15531e6b36a389",
            "keyword": "6c620862db494ed05e69356ba30e604b167b0670",
            "content": "3f176b7fe752524cec21a763aa55567e41181e07",
        }),
        (("http://www.bobx.com/idol/nashiko-momotsuki"
          "/photoset/wpb-net-_221---2018-08---magic-of-summer-0-10-10.html"), {
            "url": "f5d6c0cd0881ae6f504c21a90d86e3464dc54e8e",
            "keyword": "f4819c75f494044348889ecd27771508464c0f5f",
        }),
    )

    def items(self):
        num = 0
        while True:
            url = "{}/{}-{}-10-8.html".format(self.root, self.path, num)
            page = self.request(url, encoding="utf-8").text

            if num == 0:
                data = self.metadata(page)
                yield Message.Version, 1
                yield Message.Directory, data
                data["num"] = 0

            for url in self.images(page):
                url = text.urljoin(self.root, url.replace("-preview-", "-"))
                data = text.nameext_from_url(url, data)
                data["image_id"] = text.parse_int(
                    data["filename"].rpartition("-")[2])
                data["num"] += 1
                yield Message.Url, url, data

            num += self.per_page
            if num >= data["count"]:
                return

    @staticmethod
    def metadata(page):
        """Collect metadata for extractor-job"""
        info = text.extract(page, "<title>", "</title>")[0]
        model, _, info = info.partition(" in ")
        info, _, count = info.rpartition(" of ")
        title = info.rpartition(" - @")[0]
        return {
            "title": text.unquote(title),
            "model": text.unquote(model),
            "count": text.parse_int(count),
        }

    @staticmethod
    def images(page):
        """Extract all image-urls"""
        page = text.extract(page, "<table CELLPADDING=", "<script ")[0]
        return text.extract_iter(page, '<img src="/thumbnail', '"')


class BobxIdolExtractor(BobxExtractor):
    """Extractor for an idol's image galleries on bobx.com"""
    subcategory = "idol"
    pattern = r"(?:https?://)?(?:www\.)?bobx\.com/([^/]+/[^/?&#]+)/?$"
    test = ("http://www.bobx.com/idol/rin-okabe/", {
        "url": "74d80bfcd53b738b31909bb42e5cc97c41b475b8",
    })

    def items(self):
        url = "{}/{}/".format(self.root, self.path)
        data = {"_extractor": BobxGalleryExtractor}
        page = self.request(url).text
        skip = True

        yield Message.Version, 1
        for part in text.extract_iter(page, '="photoset/', '"'):
            # skip every other entry
            skip = not skip
            if skip:
                continue
            yield Message.Queue, "{}photoset/{}".format(url, part), data
