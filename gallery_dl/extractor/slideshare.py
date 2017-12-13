# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann, Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.slideshare.net/"""

from .common import Extractor, Message
from .. import text


class SlideshareExtractor(Extractor):
    """Extractor for images from a presentation on slideshare.net"""
    category = "slideshare"
    subcategory = "presentation"
    directory_fmt = ["{category}", "{user}"]
    filename_fmt = "{presentation}-{num}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.)?slideshare\.net/"
               r"([^/]+)/([^/]+)"]
    test = [
        ("https://www.slideshare.net/Slideshare/get-started-with-slide-share", {
            "url": "23685fb9b94b32c77a547d45dc3a82fe7579ea18",
            "content": "ee54e54898778e92696a7afec3ffabdbd98eb0cc",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.user, self.presentation = match.groups()

    def items(self):
        page = self.request("https://www.slideshare.net/" + self.user + "/" + self.presentation).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        metadata = {}

        text.extract_all(page, (
            ('title', '<title>', '</title>'),
            ('description', '<meta name="description" content="', '">'),
        ), values=metadata)

        metadata["presentation"] = self.presentation
        metadata["user"] = self.user

        return metadata

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image-urls"""
        return list(text.extract_iter(page, 'data-full="', '"'))
