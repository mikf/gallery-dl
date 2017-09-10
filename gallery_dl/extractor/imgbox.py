# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://imgbox.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text, exception
import re


class ImgboxGalleryExtractor(AsynchronousExtractor):
    """Extractor for image galleries from imgbox.com"""
    category = "imgbox"
    subcategory = "gallery"
    directory_fmt = ["{category}", "{title} - {gallery_key}"]
    filename_fmt = "{num:>03}-{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/g/([A-Za-z0-9]{10})"]
    test = [
        ("https://imgbox.com/g/JaX5V5HX7g", {
            "url": "6eafdeebaf0774238dddc9227e2ba315e40e9b7c",
            "keyword": "abe510221e1dc8c804296be25adf1498fb93f892",
            "content": "d20307dc8511ac24d688859c55abf2e2cc2dd3cc",
        }),
        ("https://imgbox.com/g/JaX5V5HX7h", {
            "exception": exception.NotFoundError,
        }),
    ]
    url_base = "https://imgbox.com"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.key = match.group(1)
        self.metadata = {}

    def items(self):
        page = self.request(self.url_base + "/g/" + self.key).text
        if "The specified gallery could not be found." in page:
            raise exception.NotFoundError("gallery")
        self.metadata = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, self.metadata
        for match in re.finditer(r'<a href="([^"]+)"><img alt="', page):
            imgpage = self.request(self.url_base + match.group(1)).text
            data = self.get_file_metadata(imgpage)
            if data["filename"]:
                data = text.nameext_from_url(data["filename"], data)
                yield Message.Url, self.get_file_url(imgpage), data

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<h1>", "</h1>")[0]
        title, _, count = title.rpartition(" - ")
        return {
            "gallery_key": self.key,
            "title": text.unescape(title),
            "count": count[:-7],
        }

    def get_file_metadata(self, page):
        """Collect metadata for a downloadable file"""
        return text.extract_all(page, (
            ("num"      , '</a> &nbsp; ', ' of '),
            (None       , 'class="image-container"', ''),
            ("image_key", 'alt="', '"'),
            ("filename" , ' title="', '"'),
        ), values=self.metadata.copy())[0]

    @staticmethod
    def get_file_url(page):
        """Extract download-url"""
        base = "https://i.imgbox.com/"
        path = text.extract(page, base, '"')[0]
        return base + path


class ImgboxImageExtractor(Extractor):
    """Extractor for single images from imgbox.com"""
    category = "imgbox"
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/([A-Za-z0-9]{8})"]
    test = [
        ("https://imgbox.com/qHhw7lpG", {
            "url": "b9556dc307edf88e016fbced6d354702bc236070",
            "keyword": "a5cdcdf6e784bb186ed65a0cd7978ae2d0e17a12",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("https://imgbox.com/qHhw7lpH", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.key = match.group(1)

    def items(self):
        page = self.request("https://imgbox.com/" + self.key).text
        url , pos = text.extract(page, 'src="https://i.', '"')
        if not url:
            raise exception.NotFoundError("image")
        filename, pos = text.extract(page, ' title="', '"', pos)
        data = text.nameext_from_url(filename, {"image_key": self.key})
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, "https://i." + url, data
