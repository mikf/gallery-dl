# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.com/"""

from .common import GalleryExtractor, Message
from .. import text


class UrlgalleriesGalleryExtractor(GalleryExtractor):
    """Extractor for urlgalleries.com galleries"""
    category = "urlgalleries"
    root = "https://urlgalleries.com"
    parent = True
    request_interval = (0.5, 1.5)
    pattern = (r"(?:https?://)?(?:\w+\.)?urlgalleries\.com"
               r"/([^/?#]+)/(\d+)(/[^/?#]+)?")
    example = "https://urlgalleries.com/BLOG/12345/TITLE"

    def items(self):
        blog, self.gallery_id, slug = self.groups
        url = f"{self.root}/{blog}/{self.gallery_id}{slug or ''}/?a=10000"
        page = self.request(url).text

        imgs = self.images(page)
        data = self.metadata(page)
        data["count"] = len(imgs)

        if ". Published by " in (desc := data.pop("_desc")):
            data["blog"] = text.extr(desc, ". Published by ", ".")

        root = self.root
        yield Message.Directory, "", data
        for data["num"], img in enumerate(imgs, 1):
            page = self.request(root + img).text
            url = text.extr(page, ' IMAGE_URL = "', '"')
            yield Message.Queue, url, data

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": self.gallery_id,
            "_desc": extr(
                'property="og:description" content="', '"'),
            "date" : self.parse_datetime_iso(
                extr('"datePublished":"', '"')),
            "blog" : text.unescape(extr(
                '"@type":"ListItem","position":2,"name":"', '"')),
            "title": text.unescape(extr(
                '"@type":"ListItem","position":3,"name":"', '"').strip()),
            "tags" : text.split_html(
                extr('<div class="badgeCatsInner"', '</div>'))[1:],
        }

    def images(self, page):
        imgs = text.extr(page, '<section ', "</section>")
        return list(text.extract_iter(imgs, ' href="', '"'))
