# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pornstars.tube/"""

from .common import GalleryExtractor
from .. import text


class PornstarsTubeGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from pornstars.tube"""
    root = "https://pornstars.tube"
    category = "pornstarstube"
    pattern = r"(?:https?://)?(?:www\.)?(pornstars\.tube/albums/(\d+))/[\w-]+"
    example = "https://pornstars.tube/albums/40771/cleaning-leads-to-delicious-mess/"

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        self.page_url = match[0]

    def metadata(self, page):
        return {
            "gallery_id": self.match[2],
            "title": text.extract(page, '<title>', ' - PORNSTARS.TUBE</title>')[0],
        }

    def images(self, page):
        page = self.request(self.page_url).text
        for url in text.extract_iter(page, ' href="', '" class="img-holder lg-lg"'):
            yield url, None
