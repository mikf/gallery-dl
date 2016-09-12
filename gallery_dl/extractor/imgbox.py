# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at http://imgbox.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text
import re

class ImgboxGalleryExtractor(AsynchronousExtractor):
    """Extractor for image galleries from imgbox.com"""
    category = "imgbox"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{title} - {gallery-key}"]
    filename_fmt = "{num:>03}-{name}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/g/([A-Za-z0-9]{10})"]
    url_base = "http://imgbox.com"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.key = match.group(1)
        self.metadata = {}

    def items(self):
        page = self.request(self.url_base + "/g/" + self.key).text
        self.metadata = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, self.metadata
        for match in re.finditer(r'<a href="([^"]+)"><img alt="', page):
            imgpage = self.request(self.url_base + match.group(1)).text
            yield Message.Url, self.get_file_url(imgpage), self.get_file_metadata(imgpage)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        match = re.search(r"<h1>(.+) \(([^ ]+) ([^ ]+) \w+\) - (\d+)", page)
        return {
            "category": self.category,
            "gallery-key": self.key,
            "title": match.group(1),
            "date": match.group(2),
            "time": match.group(3),
            "count": match.group(4),
        }

    def get_file_metadata(self, page):
        """Collect metadata for a downloadable file"""
        return text.extract_all(page, (
            ("num"      , '</a> &nbsp; ', ' of '),
            ("image-key", '/i.imgbox.com/', '?download'),
            ("name"     , ' title="', '"'),
        ), values=self.metadata.copy())[0]

    @staticmethod
    def get_file_url(page):
        """Extract download-url"""
        base = "http://i.imgbox.com/"
        path = text.extract(page, base, '"')[0]
        return base + path


class ImgboxImageExtractor(Extractor):
    """Extractor for single images from imgbox.com"""
    category = "imgbox"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/([A-Za-z0-9]{8})"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.key = match.group(1)

    def items(self):
        page = self.request("http://imgbox.com/" + self.key).text
        url     , pos = text.extract(page, 'src="http://i.', '"')
        filename, pos = text.extract(page, ' title="', '"', pos)
        data = {"category": self.category, "image-key": self.key}
        text.nameext_from_url(filename, data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, "http://i." + url, data
