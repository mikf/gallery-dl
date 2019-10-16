# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.adultempire.com/"""

from .common import GalleryExtractor
from .. import text


class AdultempireGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from www.adultempire.com"""
    category = "adultempire"
    root = "https://www.adultempire.com"
    pattern = (r"(?:https?://)?(?:www\.)?adult(?:dvd)?empire\.com"
               r"(/(\d+)/gallery\.html)")
    test = (
        ("https://www.adultempire.com/5998/gallery.html", {
            "range": "1",
            "keyword": "5b3266e69801db0d78c22181da23bc102886e027",
            "content": "5c6beb31e5e3cdc90ee5910d5c30f9aaec977b9e",
        }),
        ("https://www.adultdvdempire.com/5683/gallery.html", {
            "url": "b12cd1a65cae8019d837505adb4d6a2c1ed4d70d",
            "keyword": "8d448d79c4ac5f5b10a3019d5b5129ddb43655e5",
        }),
    )

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.gallery_id = match.group(2)

    def metadata(self, page):
        extr = text.extract_from(page, page.index('<div id="content">'))
        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title"     : text.unescape(extr('title="', '"')),
            "studio"    : extr(">studio</small>", "<").strip(),
            "date"      : text.parse_datetime(extr(
                ">released</small>", "<").strip(), "%m/%d/%Y"),
            "actors"    : sorted(text.split_html(extr(
                '<ul class="item-details item-cast-list ', '</ul>'))[1:]),
        }

    def images(self, page):
        params = {"page": 1}
        while True:
            urls = list(text.extract_iter(page, 'rel="L"><img src="', '"'))
            for url in urls:
                yield url.replace("_200.", "_9600."), None
            if len(urls) < 24:
                return
            params["page"] += 1
            page = self.request(self.gallery_url, params=params).text
