# -*- coding: utf-8 -*-

# Copyright 2018-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.myportfolio.com/"""

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
               r"(?:https?://)?(?!cdn\.)([\w-]+\.myportfolio\.com))"
               r"(/[^/?#]+)?")
    example = "https://USER.myportfolio.com/TITLE"

    def items(self):
        domain_alt, domain, path = self.groups
        if domain is None:
            domain = domain_alt
            prefix = "myportfolio:"
        else:
            prefix = ""

        url = f"https://{domain}{path or ''}"
        response = self.request(url)
        if response.history and response.url.endswith(".adobe.com/missing"):
            raise self.exc.NotFoundError()
        page = response.text

        projects = text.extr(
            page, '<section class="project-covers', '</section>')

        if projects:
            data = {"_extractor": MyportfolioGalleryExtractor}
            base = f"{prefix}https://{domain}"
            for path in text.extract_iter(projects, ' href="', '"'):
                yield Message.Queue, base + path, data
        else:
            data = self.metadata(page)
            imgs = self.images(page)
            data["count"] = len(imgs)
            yield Message.Directory, "", data
            for data["num"], url in enumerate(imgs, 1):
                yield Message.Url, url, text.nameext_from_url(url, data)

    def metadata(self, page):
        """Collect general image metadata"""
        # og:title contains data as "<user> - <title>", but both
        # <user> and <title> can contain a "-" as well, so we get the title
        # from somewhere else and cut that amount from the og:title content

        extr = text.extract_from(page)
        user = extr('property="og:title" content="', '"') or \
            extr('property=og:title content="', '"')
        descr = extr('property="og:description" content="', '"') or \
            extr('property=og:description content="', '"')
        title = extr('<h1 ', '</h1>')

        if title:
            title = title.partition(">")[2]
            user = user[:-len(title)-3]
        elif user:
            user, _, title = user.partition(" - ")
        else:
            raise self.exc.NotFoundError()

        return {
            "user": text.unescape(user),
            "title": text.unescape(title),
            "description": text.unescape(descr),
        }

    def images(self, page):
        """Extract and return a list of all image-urls"""
        return (
            list(text.extract_iter(page, 'js-lightbox" data-src="', '"')) or
            list(text.extract_iter(page, 'data-src="', '"'))
        )
