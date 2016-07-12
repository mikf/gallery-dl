# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at http://www.imagebam.com/"""

from .common import AsynchronousExtractor, Message
from .. import text

class ImagebamExtractor(AsynchronousExtractor):

    category = "imagebam"
    directory_fmt = ["{category}", "{title} - {gallery-key}"]
    filename_fmt = "{num:>03}-{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imagebam\.com/gallery/([^/]+).*"]
    url_base = "http://www.imagebam.com"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.gkey = match.group(1)

    def items(self):
        data = self.get_job_metadata()
        data["num"] = 0
        yield Message.Version, 1
        yield Message.Directory, data
        for image_url, image_id in self.get_images(data["first-url"]):
            data["id"] = image_id
            data["num"] += 1
            text.nameext_from_url(image_url, data)
            yield Message.Url, image_url, data.copy()

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        url = self.url_base + "/gallery/" + self.gkey
        page = self.request(url, encoding="utf-8").text
        data = {
            "category": self.category,
            "gallery-key": self.gkey,
        }
        data, _ = text.extract_all(page, (
            (None       , "<img src='/img/icons/photos.png'", ""),
            ("title"    , "'> ", " <"),
            ("count"    , "'>", " images"),
            ("first-url", "<a href='http://www.imagebam.com", "'"),
        ), values=data)
        return data

    def get_images(self, url):
        done = False
        while not done:
            page = self.request(self.url_base + url).text
            _  , pos = text.extract(page, 'class="btn btn-default" title="Next">', '')
            if pos == 0:
                done = True
            else:
                url, pos = text.extract(page, ' href="', '"', pos-70)
            image_id , pos = text.extract(page, '<img class="image" id="', '"', pos)
            image_url, pos = text.extract(page, ' src="', '"', pos)
            yield image_url, image_id
