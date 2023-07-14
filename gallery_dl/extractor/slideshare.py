# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann, Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.slideshare.net/"""

from .common import GalleryExtractor
from .. import text, util


class SlidesharePresentationExtractor(GalleryExtractor):
    """Extractor for images from a presentation on slideshare.net"""
    category = "slideshare"
    subcategory = "presentation"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{presentation}-{num:>02}.{extension}"
    archive_fmt = "{presentation}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?slideshare\.net"
               r"/(?:mobile/)?([^/?#]+)/([^/?#]+)")
    test = (
        (("https://www.slideshare.net"
          "/Slideshare/get-started-with-slide-share"), {
            "pattern": r"https://image\.slidesharecdn\.com/getstartedwithslide"
                       r"share-150520173821-lva1-app6892/95/get-started-with-s"
                       r"lide-share-\d+-1024\.jpg\?cb=\d+",
            "count": 19,
            "content": "2b6a191eab60b3978fdacfecf2da302dd45bc108",
            "keyword": {
                "description": "Get Started with SlideShare - "
                               "A Beginngers Guide for Creators",
                "likes": int,
                "presentation": "get-started-with-slide-share",
                "date": "dt:2015-05-20 17:38:21",
                "title": "Getting Started With SlideShare",
                "user": "Slideshare",
                "views": int,
            },
        }),
        # long title and description
        (("https://www.slideshare.net/pragmaticsolutions/warum-sie-nicht-ihren"
          "-mitarbeitenden-ndern-sollten-sondern-ihr-managementsystem"), {
            "url": "d8952260f8bec337dd809a958ec8091350393f6b",
            "keyword": {
                "title": "Warum Sie nicht Ihren Mitarbeitenden ändern "
                         "sollten, sondern Ihr Managementsystem",
                "description": "Mitarbeitende verhalten sich mehrheitlich so, "
                               "wie das System es ihnen vorgibt. Welche Voraus"
                               "setzungen es braucht, damit Ihre Mitarbeitende"
                               "n ihr ganzes Herzblut einsetzen, bespricht Fre"
                               "di Schmidli in diesem Referat.",
            },
        }),
        # mobile URL
        (("https://www.slideshare.net"
          "/mobile/uqudent/introduction-to-fixed-prosthodontics"), {
            "url": "72c431cb1eccbb6794f608ecbbc01d52e8768159",
        }),
    )

    def __init__(self, match):
        self.user, self.presentation = match.groups()
        url = "https://www.slideshare.net/{}/{}".format(
            self.user, self.presentation)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        data = util.json_loads(text.extr(
            page, 'id="__NEXT_DATA__" type="application/json">', '</script>'))
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
        parts = self.slideshow["slideImages"][0]["baseUrl"].split("/")

        begin = "{}/95/{}-".format(
            "/".join(parts[:4]),
            self.slideshow["strippedTitle"],
        )
        end = "-1024.jpg?" + parts[-1].rpartition("?")[2]

        return [
            (begin + str(n) + end, None)
            for n in range(1, self.slideshow["totalSlides"]+1)
        ]
