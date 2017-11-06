# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.imagebam.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text


class ImagebamGalleryExtractor(AsynchronousExtractor):
    """Extractor for image galleries from imagebam.com"""
    category = "imagebam"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{title} - {gallery_key}"]
    filename_fmt = "{num:>03}-{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imagebam\.com/gallery/([^/]+)"]
    test = [(("http://www.imagebam.com/"
              "gallery/adz2y0f9574bjpmonaismyrhtjgvey4o"), {
        "url": "d7a4483b6d5ebba81950a349aad58ae034c60eda",
        "keyword": "0ab7bef5cf995d9229dc900dc508311cefb32306",
        "content": "596e6bfa157f2c7169805d50075c2986549973a8",
    })]
    root = "http://www.imagebam.com"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.gkey = match.group(1)

    def items(self):
        data, url = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        data["num"] = 0
        for image_url, image_id in self.get_images(url):
            data["image_id"] = image_id
            data["num"] += 1
            text.nameext_from_url(image_url, data)
            yield Message.Url, image_url, data.copy()

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        url = self.root + "/gallery/" + self.gkey
        page = self.request(url, encoding="utf-8").text
        data, pos = text.extract_all(page, (
            (None       , "<img src='/img/icons/photos.png'", ""),
            ("title"    , "'> ", " <"),
            ("count"    , "'>", " images"),
        ), values={"gallery_key": self.gkey})
        url, pos = text.extract(
            page, "<a href='http://www.imagebam.com", "'", pos)
        return data, url

    def get_images(self, url):
        """Yield all image-urls and -ids for a gallery"""
        done = False
        while not done:
            page = self.request(self.root + url).text
            pos = text.extract(
                page, 'class="btn btn-default" title="Next">', ''
            )[1]
            if pos == 0:
                done = True
            else:
                url, pos = text.extract(page, ' href="', '"', pos-70)
            image_id , pos = text.extract(page, 'class="image" id="', '"', pos)
            image_url, pos = text.extract(page, 'src="', '"', pos)
            yield image_url, image_id


class ImagebamImageExtractor(Extractor):
    """Extractor for single images from imagebam.com"""
    category = "imagebam"
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?imagebam\.com/image/([0-9a-f]{15})"]
    test = [("http://www.imagebam.com/image/94d56c502511890", {
        "url": "94add9417c685d113a91bcdda4916e9538b5f8a9",
        "keyword": "fd99b2f45b761d0b639af46740aacd976f5dfcc7",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        page = self.request("http://www.imagebam.com/image/" + self.token).text
        iurl = text.extract(page, 'property="og:image" content="', '"')[0]
        data = text.nameext_from_url(iurl, {"token": self.token})
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, iurl, data
