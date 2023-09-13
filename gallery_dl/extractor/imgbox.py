# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgbox.com/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, exception
import re


class ImgboxExtractor(Extractor):
    """Base class for imgbox extractors"""
    category = "imgbox"
    root = "https://imgbox.com"

    def items(self):
        data = self.get_job_metadata()
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
        return text.extr(page, 'property="og:image" content="', '"')


class ImgboxGalleryExtractor(AsynchronousMixin, ImgboxExtractor):
    """Extractor for image galleries from imgbox.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{title} - {gallery_key}")
    filename_fmt = "{num:>03}-{filename}.{extension}"
    archive_fmt = "{gallery_key}_{image_key}"
    pattern = r"(?:https?://)?(?:www\.)?imgbox\.com/g/([A-Za-z0-9]{10})"
    example = "https://imgbox.com/g/12345abcde"

    def __init__(self, match):
        ImgboxExtractor.__init__(self, match)
        self.gallery_key = match.group(1)
        self.image_keys = []

    def get_job_metadata(self):
        page = self.request(self.root + "/g/" + self.gallery_key).text
        if "The specified gallery could not be found." in page:
            raise exception.NotFoundError("gallery")
        self.image_keys = re.findall(r'<a href="/([^"]+)"><img alt="', page)

        title = text.extr(page, "<h1>", "</h1>")
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
    pattern = r"(?:https?://)?(?:www\.)?imgbox\.com/([A-Za-z0-9]{8})"
    example = "https://imgbox.com/1234abcd"

    def __init__(self, match):
        ImgboxExtractor.__init__(self, match)
        self.image_key = match.group(1)

    def get_image_keys(self):
        return (self.image_key,)

    @staticmethod
    def get_image_metadata(page):
        data = ImgboxExtractor.get_image_metadata(page)
        if not data["filename"]:
            raise exception.NotFoundError("image")
        return data
