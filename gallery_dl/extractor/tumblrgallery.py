# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://tumblrgallery.xyz/"""

from .common import GalleryExtractor
from .. import text


class TumblrgalleryGalleryExtractor(GalleryExtractor):
    """Base class for tumblrgallery extractors"""
    category = "tumblrgallery"
    root = "https://www.tumblrgallery.xyz"
    pattern = (r"(?:https?://)tumblrgallery\.xyz"
               r"(/tumblrblog/gallery/(\d+).html)")
    test = (
        "https://tumblrgallery.xyz/tumblrblog/gallery/103975.html", {
            "pattern": r"/tumblrblog/gallery/103975.html"
                       r"103975",
        }
    )

    filename_fmt = "{category}_{gallery_id}_{num:>03}_{id}.{extension}"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    cookiedomain = None

    def __init__(self, match):
        self.gallery_id = text.parse_int(match.group(2))
        GalleryExtractor.__init__(self, match)

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        return {
            "title" : text.unescape(text.extract(page, "<h1>", "</h1>"))[0],
            "gallery_id": self.gallery_id,
        }

    def images(self, _):
        pageNum = 1
        while True:
            response = self.request(
                "{}/tumblrblog/gallery/{}/{}.html"
                .format(self.root, self.gallery_id, pageNum),
                allow_redirects=False
            )
            if response.status_code != 200:
                return

            page = response.text
            pageNum += 1

            urls = list(text.extract_iter(
                page,
                '<div class="report xx-co-me"> <a href="',
                '" data-fancybox="gallery"'
            ))

            for image_src in urls:
                yield image_src, {
                    "id": text.extract(image_src, "tumblr_", "_")[0]
                }
