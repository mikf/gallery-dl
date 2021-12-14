# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://imgth.com/"""

from .common import Extractor, Message
from .. import text


class ImgthGalleryExtractor(Extractor):
    """Extractor for image galleries from imgth.com"""
    category = "imgth"
    subcategory = "gallery"
    directory_fmt = ("{category}", "{gallery_id} {title}")
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    archive_fmt = "{gallery_id}_{num}"
    pattern = r"(?:https?://)?imgth\.com/gallery/(\d+)"
    test = ("http://imgth.com/gallery/37/wallpaper-anime", {
        "url": "4ae1d281ca2b48952cf5cca57e9914402ad72748",
        "keyword": "6f8c00d6849ea89d1a028764675ec1fe9dbd87e2",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.gid = match.group(1)
        self.url_base = "https://imgth.com/gallery/" + self.gid + "/g/page/"

    def items(self):
        page = self.request(self.url_base + "0").text
        data = self.metadata(page)
        yield Message.Directory, data
        for data["num"], url in enumerate(self.images(page), 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def images(self, page):
        """Yield all image urls for this gallery"""
        pnum = 0
        while True:
            thumbs = text.extract(page, '<ul class="thumbnails">', '</ul>')[0]
            for url in text.extract_iter(thumbs, '<img src="', '"'):
                yield "https://imgth.com/images" + url[24:]
            if '<li class="next">' not in page:
                return
            pnum += 1
            page = self.request(self.url_base + str(pnum)).text

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        return text.extract_all(page, (
            ("title", '<h1>', '</h1>'),
            ("count", 'total of images in this gallery: ', ' '),
            ("date" , 'created on ', ' by <'),
            (None   , 'href="/users/', ''),
            ("user" , '>', '<'),
        ), values={"gallery_id": self.gid})[0]
