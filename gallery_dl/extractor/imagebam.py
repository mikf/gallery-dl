# -*- coding: utf-8 -*-

# Copyright 2014-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.imagebam.com/"""

from .common import Extractor, Message
from .. import text, exception


class ImagebamExtractor(Extractor):
    """Base class for imagebam extractors"""
    category = "imagebam"
    root = "https://www.imagebam.com"
    cookies = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)
        if self.cookies:
            self.session.cookies = self.cookies

    def get_image_data(self, data):
        page_url = "{}/image/{}".format(self.root, data["image_key"])
        page = self.request(page_url).text
        image_url, pos = text.extract(page, '<img src="https://images', '"')

        if not image_url:
            # cache cookies
            ImagebamExtractor.cookies = self.session.cookies
            # repeat request to get past "Continue to your image" pages
            page = self.request(page_url).text
            image_url, pos = text.extract(
                page, '<img src="https://images', '"')

        filename = text.unescape(text.extract(page, 'alt="', '"', pos)[0])
        data["url"] = "https://images" + image_url
        data["filename"], _, data["extension"] = filename.rpartition(".")


class ImagebamGalleryExtractor(ImagebamExtractor):
    """Extractor for image galleries from imagebam.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title} {gallery_key}")
    filename_fmt = "{num:>03} {filename}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = r"(?:https?://)?(?:www\.)?imagebam\.com/gallery/([0-9a-z]+)"
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
    )

    def items(self):
        url = "{}/gallery/{}".format(self.root, self.key)
        page = self.request(url).text

        data = self.get_metadata(page)
        keys = self.get_image_keys(page)
        keys.reverse()
        data["count"] = len(keys)
        data["gallery_key"] = self.key

        yield Message.Directory, data
        for data["num"], data["image_key"] in enumerate(keys, 1):
            self.get_image_data(data)
            yield Message.Url, data["url"], data

    @staticmethod
    def get_metadata(page):
        """Return gallery metadata"""
        title = text.extract(page, 'id="gallery-name">', '<')[0]
        return {"title": text.unescape(title.strip())}

    def get_image_keys(self, page):
        """Return a list of all image keys"""
        keys = []
        while True:
            keys.extend(text.extract_iter(
                page, '<a href="https://www.imagebam.com/image/', '"'))
            pos = page.find('rel="next" aria-label="Next')
            if pos > 0:
                url = text.rextract(page, 'href="', '"', pos)[0]
                if url:
                    page = self.request(url).text
                    continue
            return keys


class ImagebamImageExtractor(ImagebamExtractor):
    """Extractor for single images from imagebam.com"""
    subcategory = "image"
    archive_fmt = "{image_key}"
    pattern = (r"(?:https?://)?(?:\w+\.)?imagebam\.com"
               r"/(?:image/|(?:[0-9a-f]{2}/){3})([0-9a-f]+)")
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
    )

    def items(self):
        data = {"image_key": self.key}
        self.get_image_data(data)
        yield Message.Directory, data
        yield Message.Url, data["url"], data
