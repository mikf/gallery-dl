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
    test = [("http://imgbox.com/g/JaX5V5HX7g", {
        "url": "c7c3466dde31d4308833816961104c7d1100368d",
        "keyword": "23deb783d3afee090f61472b495e797c8f262b93",
        "content": "d20307dc8511ac24d688859c55abf2e2cc2dd3cc",
    })]
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
            data = self.get_file_metadata(imgpage)
            data = text.nameext_from_url(data["filename"], data)
            yield Message.Url, self.get_file_url(imgpage), data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<h1>", "</h1>")[0]
        parts = title.rsplit(" - ", maxsplit=1)
        return {
            "gallery-key": self.key,
            "title": text.unescape(parts[0]),
            "count": parts[1][:-7],
        }

    def get_file_metadata(self, page):
        """Collect metadata for a downloadable file"""
        return text.extract_all(page, (
            ("num"      , '</a> &nbsp; ', ' of '),
            (None       , 'class="image-container"', ''),
            ("image-key", 'alt="', '"'),
            ("filename" , ' title="', '"'),
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
    test = [("http://imgbox.com/qHhw7lpG", {
        "url": "d96990ea12223895287d139695077b70dfa0abe4",
        "keyword": "c5e87be93fec3122151edf85b6424d1871279590",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.key = match.group(1)

    def items(self):
        page = self.request("http://imgbox.com/" + self.key).text
        url     , pos = text.extract(page, 'src="http://i.', '"')
        filename, pos = text.extract(page, ' title="', '"', pos)
        data = text.nameext_from_url(filename, {"image-key": self.key})
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, "http://i." + url, data
