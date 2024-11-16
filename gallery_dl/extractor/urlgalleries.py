# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://urlgalleries.net/"""

from .. import exception
from .. import text
from .common import GalleryExtractor
from .common import Message


class UrlgalleriesGalleryExtractor(GalleryExtractor):
    """Base class for Urlgalleries extractors"""

    category = "urlgalleries"
    root = "https://urlgalleries.net"
    request_interval = (0.5, 1.5)
    pattern = r"(?:https?://)(?:(\w+)\.)?urlgalleries\.net/(?:[\w-]+-)?(\d+)"
    example = "https://BLOG.urlgalleries.net/gallery-12345/TITLE"

    def items(self):
        blog, self.gallery_id = self.groups
        url = f"https://{blog}.urlgalleries.net/porn-gallery-{self.gallery_id}/?a=10000"

        with self.request(url, allow_redirects=False, fatal=...) as response:
            if 300 <= response.status_code < 500:
                if response.headers.get("location", "").endswith("/not_found_adult.php"):
                    raise exception.NotFoundError("gallery")
                raise exception.HttpError(None, response)
            page = response.text

        imgs = self.images(page)
        data = self.metadata(page)
        data["count"] = len(imgs)

        root = f"https://{blog}.urlgalleries.net"
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
            "blog": text.unescape(extr(' title="', '"')),
            "_rprt": extr(' title="', '"'),  # report button
            "title": text.unescape(extr(' title="', '"').strip()),
            "date": text.parse_datetime(extr(" images in gallery | ", "<"), "%B %d, %Y %H:%M"),
        }

    def images(self, page):
        imgs = text.extr(page, 'id="wtf"', "</div>")
        return list(text.extract_iter(imgs, " href='", "'"))
