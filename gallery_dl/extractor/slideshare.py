# -*- coding: utf-8 -*-

# Copyright 2016-2021 Mike Fährmann, Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.slideshare.net/"""

from .common import Extractor, Message
from .. import text


class SlidesharePresentationExtractor(Extractor):
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
            "url": "23685fb9b94b32c77a547d45dc3a82fe7579ea18",
            "content": "ee54e54898778e92696a7afec3ffabdbd98eb0cc",
        }),
        # long title
        (("https://www.slideshare.net/pragmaticsolutions/warum-sie-nicht-ihren"
          "-mitarbeitenden-ndern-sollten-sondern-ihr-managementsystem"), {
            "url": "cf70ca99f57f61affab47ebf8583eb564b21e3a7",
        }),
        # mobile URL
        (("https://www.slideshare.net"
          "/mobile/uqudent/introduction-to-fixed-prosthodontics"), {
            "url": "59993ad7b0cb93c73011547eedcd02c622649e9d",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user, self.presentation = match.groups()

    def items(self):
        page = self.request("https://www.slideshare.net/" + self.user +
                            "/" + self.presentation).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        descr, pos = text.extract(
            page, '<meta name="description" content="', '"')
        title, pos = text.extract(
            page, '<span class="j-title-breadcrumb">', '</span>', pos)
        views, pos = text.extract(
            page, '<span class="notranslate">', 'views<', pos)
        published, pos = text.extract(
            page, '<time datetime="', '"', pos)
        alt_descr, pos = text.extract(
            page, 'id="slideshow-description-paragraph" class="notranslate">',
            '</p>', pos)

        if descr.endswith("…") and alt_descr:
            descr = text.remove_html(alt_descr).strip()

        return {
            "user": self.user,
            "presentation": self.presentation,
            "title": text.unescape(title.strip()),
            "description": text.unescape(descr),
            "views": text.parse_int(views.replace(",", "")),
            "published": published,
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        return list(text.extract_iter(page, 'data-full="', '"'))
