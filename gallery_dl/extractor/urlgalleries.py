# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.net/"""

from .common import GalleryExtractor, Message
from .. import text


class UrlgalleriesGalleryExtractor(GalleryExtractor):
    """Base class for Urlgalleries extractors"""
    category = "urlgalleries"
    root = "urlgalleries.net"
    request_interval = (0.5, 1.0)
    pattern = r"(?:https?://)(?:(\w+)\.)?urlgalleries\.net/(?:[\w-]+-)?(\d+)"
    example = "https://blog.urlgalleries.net/gallery-12345/TITLE"

    def __init__(self, match):
        self.blog, self.gallery_id = match.groups()
        url = "https://{}.urlgalleries.net/porn-gallery-{}/?a=10000".format(
            self.blog, self.gallery_id)
        GalleryExtractor.__init__(self, match, url)

    def items(self):
        page = self.request(self.gallery_url).text
        imgs = self.images(page)
        data = self.metadata(page)
        data["count"] = len(imgs)
        del page

        root = "https://{}.urlgalleries.net".format(self.blog)
        yield Message.Directory, data
        for data["num"], img in enumerate(imgs, 1):
            response = self.request(
                root + img, method="HEAD", allow_redirects=False)
            yield Message.Queue, response.headers["Location"], data

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": self.gallery_id,
            "_site": extr(' title="', '"'),  # site name
            "blog" : text.unescape(extr(' title="', '"')),
            "_rprt": extr(' title="', '"'),  # report button
            "title": text.unescape(extr(' title="', '"').strip()),
            "date" : text.parse_datetime(
                extr(" images in gallery | ", "<"), "%B %d, %Y %H:%M"),
        }

    def images(self, page):
        imgs = text.extr(page, 'id="wtf"', "</div>")
        return list(text.extract_iter(imgs, " href='", "'"))
