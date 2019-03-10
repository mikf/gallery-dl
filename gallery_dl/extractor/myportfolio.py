# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.myportfolio.com/"""

from .common import Extractor, Message
from .. import text


class MyportfolioGalleryExtractor(Extractor):
    """Extractor for an image gallery on www.myportfolio.com"""
    category = "myportfolio"
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user}", "{title}")
    filename_fmt = "{num:>02}.{extension}"
    archive_fmt = "{user}_{filename}"
    pattern = (r"(?:myportfolio:(?:https?://)?([^/]+)|"
               r"(?:https?://)?([^.]+\.myportfolio\.com))"
               r"(/[^/?&#]+)?")
    test = (
        ("https://hannahcosgrove.myportfolio.com/robyn", {
            "url": "93b5430e765e53564b13e7d9c64c30c286011a6b",
            "keyword": "25cb3dbdad6b011242a133f30ec598318b7512e8",
        }),
        ("https://hannahcosgrove.myportfolio.com/lfw", {
            "pattern": r"https://hannahcosgrove\.myportfolio\.com/[^/?&#+]+$",
            "count": ">= 8",
        }),
        ("myportfolio:https://tooco.com.ar/6-of-diamonds-paradise-bird", {
            "count": 3,
        }),
        ("myportfolio:https://tooco.com.ar/", {
            "count": ">= 40",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        domain1, domain2, self.path = match.groups()
        self.domain = domain1 or domain2
        self.prefix = "myportfolio:" if domain1 else ""

    def items(self):
        yield Message.Version, 1
        url = "https://" + self.domain + (self.path or "")
        page = self.request(url).text

        projects = text.extract(
            page, '<section class="project-covers', '</section>')[0]

        if projects:
            data = {"_extractor": MyportfolioGalleryExtractor}
            base = self.prefix + "https://" + self.domain
            for path in text.extract_iter(projects, ' href="', '"'):
                yield Message.Queue, base + path, data
        else:
            data = self.metadata(page)
            imgs = self.images(page)
            data["count"] = len(imgs)
            yield Message.Directory, data
            for data["num"], url in enumerate(imgs, 1):
                yield Message.Url, url, text.nameext_from_url(url, data)

    @staticmethod
    def metadata(page):
        """Collect general image metadata"""
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
    def images(page):
        """Extract and return a list of all image-urls"""
        return list(text.extract_iter(page, 'js-lightbox" data-src="', '"'))
