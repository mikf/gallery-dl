# -*- coding: utf-8 -*-

# Copyright 2016-2017 Leonardo Taccari
# Copyright 2017-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.slideshare.net/"""

from .common import GalleryExtractor
from .. import text


class SlidesharePresentationExtractor(GalleryExtractor):
    """Extractor for images from a presentation on slideshare.net"""
    category = "slideshare"
    subcategory = "presentation"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{presentation}-{num:>02}.{extension}"
    archive_fmt = "{presentation}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?slideshare\.net"
               r"/(?:mobile/)?([^/?#]+)/([^/?#]+)")
    example = "https://www.slideshare.net/USER/PRESENTATION"

    def __init__(self, match):
        self.user, self.presentation = match.groups()
        url = "https://www.slideshare.net/{}/{}".format(
            self.user, self.presentation)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        data = self._extract_nextdata(page)
        self.slideshow = slideshow = data["props"]["pageProps"]["slideshow"]

        return {
            "user"        : slideshow["username"],
            "presentation": self.presentation,
            "title"       : slideshow["title"].strip(),
            "description" : slideshow["description"].strip(),
            "views"       : slideshow["views"],
            "likes"       : slideshow["likes"],
            "date"        : text.parse_datetime(
                slideshow["createdAt"], "%Y-%m-%d %H:%M:%S %Z"),
        }

    def images(self, page):
        slides = self.slideshow["slides"]
        begin = "{}/{}/95/{}-".format(
            slides["host"],
            slides["imageLocation"],
            slides["title"],
        )
        end = "-1024.jpg"

        return [
            (begin + str(n) + end, None)
            for n in range(1, self.slideshow["totalSlides"]+1)
        ]
