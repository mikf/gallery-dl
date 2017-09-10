# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
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
    directory_fmt = ["{category}", "{gallery_id} {title}"]
    filename_fmt = "{category}_{gallery_id}_{num:>03}.{extension}"
    pattern = [r"(?:https?://)?imgth\.com/gallery/(\d+)"]
    test = [("http://imgth.com/gallery/37/wallpaper-anime", {
        "url": "4ae1d281ca2b48952cf5cca57e9914402ad72748",
        "keyword": "e62d14f20ded393d28c2789fcc34ea2c30bc6a7c",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.gid = match.group(1)
        self.url = "https://imgth.com/gallery/" + self.gid + "/g/page/"

    def items(self):
        page = self.request(self.url + "0").text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(self.get_images(page), 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_images(self, page):
        """Yield all image urls for this gallery"""
        pnum = 0
        while True:
            pos = 0
            page = text.extract(page, '<ul class="thumbnails">', '</ul>')[0]
            while True:
                url, pos = text.extract(page, '<img src="', '"', pos)
                if not url:
                    break
                yield "https://imgth.com/images/" + url[24:]
            pos = page.find('<li class="next">', pos)
            if pos == -1:
                return
            pnum += 1
            page = self.request(self.url + str(pnum)).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        return text.extract_all(page, (
            ("title", '<h1>', '</h1>'),
            ("count", 'total of images in this gallery: ', ' '),
            ("date" , 'created on ', ' by <'),
            (None   , 'href="/users/', ''),
            ("user" , '>', '<'),
        ), values={"gallery_id": self.gid})[0]
