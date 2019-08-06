# -*- coding: utf-8 -*-

# Copyright 2014-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.imagebam.com/"""

from .common import Extractor, Message
from .. import text, exception


class ImagebamExtractor(Extractor):
    """Base class for imagebam extractors"""
    category = "imagebam"
    root = "http://www.imagebam.com"

    def get_image_data(self, page_url, data):
        """Fill 'data' and return image URL"""
        page = self.request(page_url).text
        image_url = text.extract(page, 'property="og:image" content="', '"')[0]
        data["extension"] = image_url.rpartition(".")[2]
        data["image_key"] = page_url.rpartition("/")[2]
        data["image_id"] = data["image_key"][6:]
        return image_url

    def request_page(self, url):
        """Retrive the main part of a gallery page"""
        page = self.request(text.urljoin(self.root, url)).text
        return text.extract(page, "<fieldset>", "</fieldset>")[0]


class ImagebamGalleryExtractor(ImagebamExtractor):
    """Extractor for image galleries from imagebam.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title} - {gallery_key}")
    filename_fmt = "{num:>03}-{image_key}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = r"(?:https?://)?(?:www\.)?imagebam\.com/gallery/([0-9a-z]+)"
    test = (
        ("http://www.imagebam.com/gallery/adz2y0f9574bjpmonaismyrhtjgvey4o", {
            "url": "76d976788ae2757ac81694736b07b72356f5c4c8",
            "keyword": "9e25b8827474ac93c54855e798d60aa3cbecbd7a",
            "content": "596e6bfa157f2c7169805d50075c2986549973a8",
        }),
        ("http://www.imagebam.com/gallery/op9dwcklwdrrguibnkoe7jxgvig30o5p", {
            #  more than 100 images; see issue #219
            "count": 107,
            "url": "32ae6fe5dc3e4ca73ff6252e522d16473595d1d1",
        }),
        ("http://www.imagebam.com/gallery/gsl8teckymt4vbvx1stjkyk37j70va2c", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        ImagebamExtractor.__init__(self, match)
        self.gallery_key = match.group(1)

    def items(self):
        url = "{}/gallery/{}".format(self.root, self.gallery_key)
        page = self.request_page(url)
        if not page or ">Error<" in page:
            raise exception.NotFoundError("gallery")

        data = self.get_metadata(page)
        imgs = self.get_image_pages(page)
        data["count"] = len(imgs)
        data["gallery_key"] = self.gallery_key

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], page_url in enumerate(imgs, 1):
            image_url = self.get_image_data(page_url, data)
            yield Message.Url, image_url, data

    @staticmethod
    def get_metadata(page):
        """Return gallery metadata"""
        return text.extract_all(page, (
            ("title"      , "'> ", " <span "),
            (None         , "'>", "</span>"),
            ("description", ":#FCFCFC;'>", "</div>"),
        ))[0]

    def get_image_pages(self, page):
        """Return a list of all image pages"""
        pages = []
        while True:
            pages.extend(text.extract_iter(page, "\n<a href='", "'"))
            pos = page.find('"pagination_current"')
            if pos > 0:
                url = text.extract(page, "<a href='", "'", pos)[0]
                if url:
                    page = self.request_page(url)
                    continue
            return pages


class ImagebamImageExtractor(ImagebamExtractor):
    """Extractor for single images from imagebam.com"""
    subcategory = "image"
    filename_fmt = "{image_key}.{extension}"
    archive_fmt = "{image_key}"
    pattern = (r"(?:https?://)?(?:\w+\.)?imagebam\.com"
               r"/(?:image/|(?:[0-9a-f]{2}/){3})([0-9a-f]+)")
    test = (
        ("http://www.imagebam.com/image/94d56c502511890", {
            "url": "5e9ba3b1451f8ded0ae3a1b84402888893915d4a",
            "keyword": "4263d4840007524129792b8587a562b5d20c2687",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("http://images3.imagebam.com/1d/8c/44/94d56c502511890.png"),
    )

    def __init__(self, match):
        ImagebamExtractor.__init__(self, match)
        self.image_key = match.group(1)

    def items(self):
        page_url = "{}/image/{}".format(self.root, self.image_key)
        data = {}
        image_url = self.get_image_data(page_url, data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, image_url, data
