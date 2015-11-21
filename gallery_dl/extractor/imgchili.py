# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from albums at http://imgchili.net/"""

from .common import Extractor, Message
from .. import text
import re

class ImgchiliExtractor(Extractor):

    category = "imgchili"
    directory_fmt = ["{category}", "{title} - {key}"]
    filename_fmt = "{num:>03}-{name}"
    pattern = [r"(?:https?://)?(?:www\.)?imgchili\.net/album/([^/]+)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.match = match
        self.num = 0

    def items(self):
        page = self.request(self.match.string).text
        yield Message.Version, 1
        yield Message.Headers, {"Referer": "http://imgchili.net/"}
        yield Message.Directory, self.get_job_metadata(page)

        pattern = r' src="http://t(\d+\.imgchili\.net/(\d+)/(\d+)_([^/"]+))"'
        for match in re.finditer(pattern, page):
            yield Message.Url, self.get_file_url(match), self.get_file_metadata(match)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<h1>", "</h1>")[0]
        return {
            "category": info["category"],
            "title": title,
            "key": self.match.group(1),
        }

    def get_file_metadata(self, match):
        """Collect metadata for a downloadable file"""
        self.num += 1
        return {
            "album-id": match.group(2),
            "image-id": match.group(3),
            "name": match.group(4),
            "num": self.num,
        }

    @staticmethod
    def get_file_url(match):
        """Extract download-url from 'match'"""
        return "http://i" + match.group(1)
