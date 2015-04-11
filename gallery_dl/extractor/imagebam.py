# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at http://www.imagebam.com/"""

from .common import AsynchronousExtractor
from .common import Message
from .common import filename_from_url

info = {
    "category": "imagebam",
    "extractor": "ImagebamExtractor",
    "directory": ["{category}", "{title} - {key}"],
    "filename": "{num:>03}-{name}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?imagebam\.com/(gallery)/([^/]+).*",
    ],
}

class ImagebamExtractor(AsynchronousExtractor):

    url_base = "http://www.imagebam.com"

    def __init__(self, match, config):
        AsynchronousExtractor.__init__(self, config)
        self.match = match
        self.num = 0
        self.metadata = {}

    def items(self):
        self.num = 0
        self.metadata = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, self.metadata

        next_url = self.metadata["first-url"]
        done = False
        while not done:
            # get current page
            text = self.request(self.url_base + next_url).text

            # get url for next page
            next_url, pos = self.extract(text, "<a class='buttonblue' href='", "'")

            # if the following text isn't "><span>next image" we are done
            if not text.startswith("><span>next image", pos):
                done = True

            # get image url
            img_url, pos = self.extract(text, 'onclick="scale(this);" src="', '"', pos)

            yield Message.Url, img_url, self.get_file_metadata(img_url)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        gallery_key = self.match.group(2)
        text = self.request(self.url_base + "/gallery/" + gallery_key).text
        _    , pos = self.extract(text, "<img src='/img/icons/photos.png'", "")
        title, pos = self.extract(text, "'> ", " <", pos)
        count, pos = self.extract(text, "'>", " images", pos)
        url  , pos = self.extract(text, "<a href='http://www.imagebam.com", "'", pos)
        return {
            "category": info["category"],
            "key": gallery_key,
            "title": title,
            "count": count,
            "first-url": url,
        }

    def get_file_metadata(self, url):
        """Collect metadata for a downloadable file"""
        self.num += 1
        data = self.metadata.copy()
        data["num"] = self.num
        data["name"] = filename_from_url(url)
        return data
