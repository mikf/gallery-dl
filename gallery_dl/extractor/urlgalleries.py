# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.net/"""

from .common import GalleryExtractor, Message
from .. import text, exception


class UrlgalleriesGalleryExtractor(GalleryExtractor):
    """Base class for Urlgalleries extractors"""
    category = "urlgalleries"
    root = "https://urlgalleries.net"
    request_interval = (0.5, 1.5)
    pattern = (r"(?:https?://)()(?:(\w+)\.)?urlgalleries\.net"
               r"/(?:b/([^/?#]+)/)?(?:[\w-]+-)?(\d+)")
    example = "https://urlgalleries.net/b/BLOG/gallery-12345/TITLE"

    def items(self):
        _, blog_alt, blog, self.gallery_id = self.groups
        if not blog:
            blog = blog_alt
        url = "https://urlgalleries.net/b/{}/porn-gallery-{}/?a=10000".format(
            blog, self.gallery_id)

        with self.request(url, allow_redirects=False, fatal=...) as response:
            if 300 <= response.status_code < 500:
                if response.headers.get("location", "").endswith(
                        "/not_found_adult.php"):
                    raise exception.NotFoundError("gallery")
                raise exception.HttpError(None, response)
            page = response.text

        imgs = self.images(page)
        data = self.metadata(page)
        data["count"] = len(imgs)

        root = "https://urlgalleries.net/b/" + blog
        yield Message.Directory, data
        for data["num"], img in enumerate(imgs, 1):
            page = self.request(root + img).text
            url = text.extr(page, "window.location.href = '", "'")
            yield Message.Queue, url, data

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
