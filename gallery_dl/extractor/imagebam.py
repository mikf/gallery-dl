# -*- coding: utf-8 -*-

# Copyright 2014-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagebam.com/"""

from .common import Extractor, Message
from .. import text, exception
import re


class ImagebamExtractor(Extractor):
    """Base class for imagebam extractors"""
    category = "imagebam"
    root = "https://www.imagebam.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)
        self.session.cookies.set("nsfw_inter", "1", domain="www.imagebam.com")

    def _parse_image_page(self, path):
        page = self.request(self.root + path).text
        url, pos = text.extract(page, '<img src="https://images', '"')
        filename = text.unescape(text.extract(page, 'alt="', '"', pos)[0])

        data = {
            "url"      : "https://images" + url,
            "image_key": path.rpartition("/")[2],
        }
        data["filename"], _, data["extension"] = filename.rpartition(".")
        return data


class ImagebamGalleryExtractor(ImagebamExtractor):
    """Extractor for imagebam galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title} {gallery_key}")
    filename_fmt = "{num:>03} {filename}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = (r"(?:https?://)?(?:www\.)?imagebam\.com"
               r"(/(?:gallery/|view/G)[a-zA-Z0-9]+)")
    test = (
        ("https://www.imagebam.com/gallery/adz2y0f9574bjpmonaismyrhtjgvey4o", {
            "url": "76d976788ae2757ac81694736b07b72356f5c4c8",
            "keyword": "b048478b1bbba3072a7fa9fcc40630b3efad1f6c",
            "content": "596e6bfa157f2c7169805d50075c2986549973a8",
        }),
        ("http://www.imagebam.com/gallery/op9dwcklwdrrguibnkoe7jxgvig30o5p", {
            #  more than 100 images; see issue #219
            "count": 107,
            "url": "32ae6fe5dc3e4ca73ff6252e522d16473595d1d1",
        }),
        ("http://www.imagebam.com/gallery/gsl8teckymt4vbvx1stjkyk37j70va2c", {
            "exception": exception.HttpError,
        }),
        # /view/ path (#2378)
        ("https://www.imagebam.com/view/GA3MT1", {
            "url": "35018ce1e00a2d2825a33d3cd37857edaf804919",
            "keyword": "3a9f98178f73694c527890c0d7ca9a92b46987ba",
        }),
    )

    def items(self):
        page = self.request(self.root + self.path).text

        images = self.images(page)
        images.reverse()

        data = self.metadata(page)
        data["count"] = len(images)
        data["gallery_key"] = self.path.rpartition("/")[2]

        yield Message.Directory, data
        for data["num"], path in enumerate(images, 1):
            image = self._parse_image_page(path)
            image.update(data)
            yield Message.Url, image["url"], image

    @staticmethod
    def metadata(page):
        return {"title": text.unescape(text.extract(
            page, 'id="gallery-name">', '<')[0].strip())}

    def images(self, page):
        findall = re.compile(r'<a href="https://www\.imagebam\.com'
                             r'(/(?:image/|view/M)[a-zA-Z0-9]+)').findall

        paths = []
        while True:
            paths += findall(page)
            pos = page.find('rel="next" aria-label="Next')
            if pos > 0:
                url = text.rextract(page, 'href="', '"', pos)[0]
                if url:
                    page = self.request(url).text
                    continue
            return paths


class ImagebamImageExtractor(ImagebamExtractor):
    """Extractor for single imagebam images"""
    subcategory = "image"
    archive_fmt = "{image_key}"
    pattern = (r"(?:https?://)?(?:\w+\.)?imagebam\.com"
               r"(/(?:image/|view/M|(?:[0-9a-f]{2}/){3})[a-zA-Z0-9]+)")
    test = (
        ("https://www.imagebam.com/image/94d56c502511890", {
            "url": "5e9ba3b1451f8ded0ae3a1b84402888893915d4a",
            "keyword": "2a4380d4b57554ff793898c2d6ec60987c86d1a1",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("http://images3.imagebam.com/1d/8c/44/94d56c502511890.png"),
        # NSFW (#1534)
        ("https://www.imagebam.com/image/0850951366904951", {
            "url": "d37297b17ed1615b4311c8ed511e50ce46e4c748",
        }),
        # /view/ path (#2378)
        ("https://www.imagebam.com/view/ME8JOQP", {
            "url": "4dca72bbe61a0360185cf4ab2bed8265b49565b8",
            "keyword": "15a494c02fd30846b41b42a26117aedde30e4ceb",
            "content": "f81008666b17a42d8834c4749b910e1dc10a6e83",
        }),
    )

    def items(self):
        path = self.path
        if path[3] == "/":
            path = ("/view/" if path[10] == "M" else "/image/") + path[10:]

        image = self._parse_image_page(path)
        yield Message.Directory, image
        yield Message.Url, image["url"], image
