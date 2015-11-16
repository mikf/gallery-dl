# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.thespectrum.net/manga_scans/"""

from .common import AsynchronousExtractor, Message
from .. import text
import os.path

info = {
    "category": "spectrumnexus",
    "extractor": "SpectrumNexusExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(view\.thespectrum\.net/series/[^\.]+.html)\?ch=Chapter\+(\d+)",
    ],
}

class SpectrumNexusExtractor(AsynchronousExtractor):

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.url = "http://" + match.group(1)
        self.chapter = match.group(2)

    def items(self):
        params = {
            "ch": "Chapter " + self.chapter,
            "page": 1,
        }
        page = self.request(self.url, params=params).text
        data = self.get_job_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data.copy()
        count = int(data["count"])
        for i in range(1, count+1):
            url = self.get_image_url(page)
            text.nameext_from_url(url, data)
            data["page"] = i
            yield Message.Url, url, data.copy()
            if i < count:
                params["page"] += 1
                page = self.request(self.url, params=params).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "category": info["category"],
            "chapter": self.chapter,
        }
        return text.extract_all(page, (
            ('manga', '<title>', ' &#183; SPECTRUM NEXUS </title>'),
            ('count', '<div class="viewerLabel"> of ', '<'),
        ), values=data)[0]

    @staticmethod
    def get_image_url(page):
        """Extract url of one manga page"""
        return text.extract(page, '<img id="mainimage" src="', '"')[0]
