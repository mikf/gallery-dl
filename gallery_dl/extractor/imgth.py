# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgth.com/"""

from .common import GalleryExtractor
from .. import text


class ImgthGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from imgth.com"""
    category = "imgth"
    root = "https://imgth.com"
    pattern = r"(?:https?://)?(?:www\.)?imgth\.com/gallery/(\d+)"
    test = (
        ("https://imgth.com/gallery/37/wallpaper-anime", {
            "url": "4ae1d281ca2b48952cf5cca57e9914402ad72748",
            "pattern": r"https://imgth\.com/images/2009/11/25"
                       r"/wallpaper-anime_\w+\.jpg",
            "keyword": {
                "count": 12,
                "date": "dt:2009-11-25 18:21:00",
                "extension": "jpg",
                "filename": r"re:wallpaper-anime_\w+",
                "gallery_id": 37,
                "num": int,
                "title": "Wallpaper anime",
                "user": "celebrities",
            },
        }),
        ("https://www.imgth.com/gallery/37/wallpaper-anime"),
    )

    def __init__(self, match):
        self.gallery_id = gid = match.group(1)
        url = "{}/gallery/{}/g/".format(self.root, gid)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": text.parse_int(self.gallery_id),
            "title": text.unescape(extr("<h1>", "</h1>")),
            "count": text.parse_int(extr(
                "total of images in this gallery: ", " ")),
            "date" : text.parse_datetime(
                extr("created on ", " by <")
                .replace("th, ", " ", 1).replace("nd, ", " ", 1)
                .replace("st, ", " ", 1), "%B %d %Y at %H:%M"),
            "user" : text.unescape(extr(">", "<")),
        }

    def images(self, page):
        pnum = 0

        while True:
            thumbs = text.extr(page, '<ul class="thumbnails">', '</ul>')
            for url in text.extract_iter(thumbs, '<img src="', '"'):
                path = url.partition("/thumbs/")[2]
                yield ("{}/images/{}".format(self.root, path), None)

            if '<li class="next">' not in page:
                return

            pnum += 1
            url = "{}/gallery/{}/g/page/{}".format(
                self.root, self.gallery_id, pnum)
            page = self.request(url).text
