# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann, Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.slideshare.net/"""

from .common import GalleryExtractor
from .. import text
import json


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
                "comments": "0",
                "description": "Get Started with SlideShare - "
                               "A Beginngers Guide for Creators",
                "likes": r"re:\d{3,}",
                "presentation": "get-started-with-slide-share",
                "published": "dt:2015-05-20 00:00:00",
                "title": "Getting Started With SlideShare",
                "user": "Slideshare",
                "views": r"re:\d{7,}",
            },
        }),
        # long title and description
        (("https://www.slideshare.net/pragmaticsolutions/warum-sie-nicht-ihren"
          "-mitarbeitenden-ndern-sollten-sondern-ihr-managementsystem"), {
            "url": "cf70ca99f57f61affab47ebf8583eb564b21e3a7",
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
            "url": "43eda2adf4dd221a251c8df794dfb82649e94647",
        }),
    )

    def __init__(self, match):
        self.user, self.presentation = match.groups()
        url = "https://www.slideshare.net/{}/{}".format(
            self.user, self.presentation)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        descr = extr('<meta name="description" content="', '"')
        comments = extr('content="UserComments:', '"')
        likes = extr('content="UserLikes:', '"')
        views = extr('content="UserPageVisits:', '"')
        title = extr('<span class="j-title-breadcrumb">', '</span>')
        published = extr('<div class="metadata-item">', '</div>')

        if descr.endswith("…"):
            alt_descr = extr('slideshow-description-text"', '</p>')
            if alt_descr:
                descr = text.remove_html(alt_descr.partition(">")[2]).strip()

        return {
            "user": self.user,
            "presentation": self.presentation,
            "title": text.unescape(title.strip()),
            "description": text.unescape(descr),
            "views": views,
            "likes": likes,
            "comments": comments,
            "published": text.parse_datetime(
                published.strip(), "%b. %d, %Y"),
        }

    @staticmethod
    def images(page):
        data = json.loads(text.extract(
            page, "xtend(true, slideshare_object.slideshow_config, ", ");")[0])

        # useing 'stripped_title' here is technically wrong, but it works all
        # the same, slideshare doesn't seem to care what characters go there
        begin = "https://image.slidesharecdn.com/{}/95/{}-".format(
            data["ppt_location"], data["stripped_title"])
        end = "-1024.jpg?cb=" + str(data["timestamp"])

        return [
            (begin + str(n) + end, None)
            for n in range(1, data["slide_count"]+1)
        ]
