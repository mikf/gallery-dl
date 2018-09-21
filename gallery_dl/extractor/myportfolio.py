# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.myportfolio.com/"""

from .common import Extractor, Message
from .. import text


BASE_PATTERN = (
    r"(?:myportfolio:(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+\.myportfolio\.com))")


class MyportfolioGalleryExtractor(Extractor):
    """Extractor for an image gallery on www.myportfolio.com"""
    category = "myportfolio"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{user}", "{title}"]
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{user}_{name}"
    pattern = [BASE_PATTERN + r"/(?!projects/?$)([^/?&#]+)"]
    test = [
        ("https://hannahcosgrove.myportfolio.com/chloe", {
            "url": "d5cf993a05439a9d8a99590aa61e14e5ac8d0cd0",
            "keyword": "cdb9ca8bdc16efa6ce04aba384f7932d1610b22f",
        }),
        ("myportfolio:https://tooco.com.ar/6-of-diamonds-paradise-bird", {
            "count": 3,
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.domain = match.group(1) or match.group(2)
        self.gallery = match.group(3)

    def items(self):
        url = "https://{}/{}".format(self.domain, self.gallery)
        page = self.request(url).text

        data = self.get_metadata(page)
        imgs = self.get_images(page)
        data["count"] = len(imgs)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    @staticmethod
    def get_metadata(page):
        """Collect metadata for extractor-job"""
        # og:title contains data as "<user> - <title>", but both
        # <user> and <title> can contain a "-" as well, so we get the title
        # from somewhere else and cut that amount from the og:title content

        user, pos = text.extract(
            page, 'property=og:title content="', '"')
        desc, pos = text.extract(
            page, 'property=og:description content="', '"', pos)
        title, pos = text.extract(
            page, '<h1 ', '</h1>', pos)

        title = title.partition(">")[2]
        user = user[:-len(title)-3]

        return {
            "user": text.unescape(user),
            "title": text.unescape(title),
            "description": text.unescape(desc or ""),
        }

    @staticmethod
    def get_images(page):
        """Extract and return a list of all image-urls"""
        return list(text.extract_iter(page, 'js-lightbox" data-src="', '"'))


class MyportfolioUserExtractor(Extractor):
    """Extractor for a user's galleries on www.myportfolio.com"""
    category = "myportfolio"
    subcategory = "user"
    pattern = [BASE_PATTERN + r"/?$"]
    test = [
        ("https://hannahcosgrove.myportfolio.com/", {
            "pattern": r"https://hannahcosgrove\.myportfolio\.com/[^/?&#+]+$",
            "count": ">= 23",
        }),
        ("myportfolio:https://tooco.com.ar/", {
            "count": ">= 40",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.domain = match.group(1) or match.group(2)
        self.prefix = "myportfolio:" if match.group(1) else ""

    def items(self):
        url = "https://" + self.domain
        page = self.request(url).text
        main = text.extract(page, "<main>", "</main>")[0]

        yield Message.Version, 1
        for path in text.extract_iter(main, ' href="', '"'):
            if path and path[0] == "/":
                yield Message.Queue, self.prefix + url + path, {}
