# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.thespectrum.net/manga_scans/"""

from .common import Extractor, AsynchronousExtractor, Message
from .. import text


class SpectrumnexusMangaExtractor(Extractor):
    """Extractor for mangas from thespectrum.net"""
    category = "spectrumnexus"
    subcategory = "manga"
    pattern = [r"(?:https?://)?view\.thespectrum\.net/series/([^\.]+)\.html$"]
    test = [("http://view.thespectrum.net/series/kare-kano-volume-01.html", {
        "url": "b2b175aad5ef1701cc4aee7c24f1ca3a93aba9cb",
    })]
    url_base = "http://view.thespectrum.net/series/"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = self.url_base + match.group(1) + ".html"

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.url + "?ch=" + chapter.replace(" ", "+")

    def get_chapters(self):
        """Return a list of all chapter identifiers"""
        page = self.request(self.url).text
        page = text.extract(
            page, '<select class="selectchapter"', '</select>'
        )[0]
        return text.extract_iter(page, '<option value="', '"')


class SpectrumnexusChapterExtractor(AsynchronousExtractor):
    """Extractor for manga-chapters or -volumes from thespectrum.net"""
    category = "spectrumnexus"
    subcategory = "chapter"
    directory_fmt = ["{category}", "{manga}", "{identifier}"]
    filename_fmt = "{manga} {identifier} {page:>03}.{extension}"
    pattern = [
        (r"(?:https?://)?(view\.thespectrum\.net/series/"
         r"[^\.]+\.html)\?ch=(Chapter\+(\d+)|Volume\+(\d+))"),
        (r"(?:https?://)?(view\.thespectrum\.net/series/"
         r"[^/]+-chapter-(\d+)\.html)"),
    ]
    test = [(("http://view.thespectrum.net/series/"
              "toriko.html?ch=Chapter+343&page=1"), {
        "url": "c0fc7dc594841217cc622a67edd79f06e9900333",
        "keyword": "8499166b62db0c87e7109cc5f9aa837b4815dd9c",
    })]

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.url = "http://" + match.group(1)
        self.identifier = match.group(2)
        self.chapter = match.group(3)
        self.volume = match.group(4)

    def items(self):
        params = {
            "ch": self.identifier,
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
            "chapter": self.chapter or "",
            "volume": self.volume or "",
            "identifier": self.identifier.replace("+", " "),
        }
        return text.extract_all(page, (
            ('manga', '<title>', ' &#183; SPECTRUM NEXUS </title>'),
            ('count', '<div class="viewerLabel"> of ', '<'),
        ), values=data)[0]

    @staticmethod
    def get_image_url(page):
        """Extract url of one manga page"""
        return text.extract(page, '<img id="mainimage" src="', '"')[0]
