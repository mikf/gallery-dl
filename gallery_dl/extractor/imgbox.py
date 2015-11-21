# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at http://imgbox.com/"""

from .common import AsynchronousExtractor, Message
from .. import text
import re

class ImgboxExtractor(AsynchronousExtractor):

    category = "imgbox"
    directory_fmt = ["{category}", "{title} - {gallery-key}"]
    filename_fmt = "{num:>03}-{name}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/g/(.+)"]
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
        data = self.metadata.copy()
        data, _ = text.extract_all(page, (
            ("num"      , '</a> &nbsp; ', ' of '),
            ("image-key", '/i.imgbox.com/', '?download'),
            ("name"     , ' title="', '"'),
        ), values=data)
        return data

    @staticmethod
    def get_file_url(page):
        """Extract download-url"""
        base = "http://i.imgbox.com/"
        path, _ = text.extract(page, base, '"')
        return base + path
