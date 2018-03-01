# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from galleries at https://imgbox.com/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text, exception
import re


class ImgboxExtractor(Extractor):
    """Base class for imgbox extractors"""
    category = "imgbox"
    root = "https://imgbox.com"

    def items(self):
        data = self.get_job_metadata()
        yield Message.Version, 1
        yield Message.Directory, data

        for image_key in self.get_image_keys():
            imgpage = self.request(self.root + "/" + image_key).text
            imgdata = self.get_image_metadata(imgpage)
            if imgdata["filename"]:
                imgdata.update(data)
                imgdata["image_key"] = image_key
                text.nameext_from_url(imgdata["filename"], imgdata)
                yield Message.Url, self.get_image_url(imgpage), imgdata

    @staticmethod
    def get_job_metadata():
        """Collect metadata for extractor-job"""
        return {}

    @staticmethod
    def get_image_keys():
        """Return an iterable containing all image-keys"""
        return []

    @staticmethod
    def get_image_metadata(page):
        """Collect metadata for a downloadable file"""
        return text.extract_all(page, (
            ("num"      , '</a> &nbsp; ', ' of '),
            (None       , 'class="image-container"', ''),
            ("filename" , ' title="', '"'),
        ))[0]

    @staticmethod
    def get_image_url(page):
        """Extract download-url"""
        pos = page.index(">Image</a>")
        return text.extract(page, '<a href="', '"', pos)[0]


class ImgboxGalleryExtractor(AsynchronousExtractor, ImgboxExtractor):
    """Extractor for image galleries from imgbox.com"""
    subcategory = "gallery"
    directory_fmt = ["{category}", "{title} - {gallery_key}"]
    filename_fmt = "{num:>03}-{name}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/g/([A-Za-z0-9]{10})"]
    test = [
        ("https://imgbox.com/g/JaX5V5HX7g", {
            "url": "678f0bca1251d810372326ea4f16582cafa800e4",
            "keyword": "92499344257cf8c72695a8dab4ccc15ca7655c1e",
            "content": "d20307dc8511ac24d688859c55abf2e2cc2dd3cc",
        }),
        ("https://imgbox.com/g/cUGEkRbdZZ", {
            "url": "d839d47cbbbeb121f83c520072512f7e51f52107",
            "keyword": "b352ca26009ba10d80b5e46067a78b4a51c6c2c9",
        }),
        ("https://imgbox.com/g/JaX5V5HX7h", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.gallery_key = match.group(1)
        self.image_keys = []

    def get_job_metadata(self):
        page = self.request(self.root + "/g/" + self.gallery_key).text
        if "The specified gallery could not be found." in page:
            raise exception.NotFoundError("gallery")
        self.image_keys = re.findall(r'<a href="/([^"]+)"><img alt="', page)

        title = text.extract(page, "<h1>", "</h1>")[0]
        title, _, count = title.rpartition(" - ")
        return {
            "gallery_key": self.gallery_key,
            "title": text.unescape(title),
            "count": count[:-7],
        }

    def get_image_keys(self):
        return self.image_keys


class ImgboxImageExtractor(ImgboxExtractor):
    """Extractor for single images from imgbox.com"""
    subcategory = "image"
    archive_fmt = "{image_key}"
    pattern = [r"(?:https?://)?(?:www\.)?imgbox\.com/([A-Za-z0-9]{8})"]
    test = [
        ("https://imgbox.com/qHhw7lpG", {
            "url": "d931f675a9b848fa7cb9077d6c2b14eb07bdb80f",
            "keyword": "a7a65a05a49d9a0eae95d637019af55faad09c5e",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
        }),
        ("https://imgbox.com/qHhw7lpH", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        ImgboxExtractor.__init__(self)
        self.image_key = match.group(1)

    def get_image_keys(self):
        return (self.image_key,)

    @staticmethod
    def get_image_metadata(page):
        data = ImgboxExtractor.get_image_metadata(page)
        if not data["filename"]:
            raise exception.NotFoundError("image")
        return data
