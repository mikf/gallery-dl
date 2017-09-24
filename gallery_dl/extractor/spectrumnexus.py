# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.thespectrum.net/manga_scans/"""

from .common import MangaExtractor, AsynchronousExtractor, Message
from .. import text, util


class SpectrumnexusMangaExtractor(MangaExtractor):
    """Extractor for manga from thespectrum.net"""
    category = "spectrumnexus"
    pattern = [r"(?:https?://)?(view\.thespectrum\.net/series/[^.]+\.html)#?$"]
    reverse = False
    test = [("http://view.thespectrum.net/series/kare-kano-volume-01.html", {
        "url": "b2b175aad5ef1701cc4aee7c24f1ca3a93aba9cb",
        "keyword": "5ed9d5c7c69d2d03417c853c4e8eae30f1e5febf",
    })]

    def chapters(self, page):
        results = []
        manga = text.extract(page, '<title>', ' &#183; ')[0]
        page = text.extract(page, 'class="selectchapter"', '</select>')[0]
        for chapter in text.extract_iter(page, '<option value="', '"'):
            results.append((self.url + "?ch=" + chapter.replace(" ", "+"), {
                "manga": manga, "chapter_string": chapter,
            }))
        return results


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
        "keyword": "3d0cb57b6b1c2cbecc7aed33f83c24891a4ff53f",
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
        for i in range(1, data["count"]+1):
            url = self.get_image_url(page)
            text.nameext_from_url(url, data)
            data["page"] = i
            yield Message.Url, url, data.copy()
            if i < data["count"]:
                params["page"] += 1
                page = self.request(self.url, params=params).text

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        data = {
            "chapter": util.safe_int(self.chapter),
            "volume": util.safe_int(self.volume),
            "identifier": self.identifier.replace("+", " "),
        }
        data = text.extract_all(page, (
            ('manga', '<title>', ' &#183; SPECTRUM NEXUS </title>'),
            ('count', '<div class="viewerLabel"> of ', '<'),
        ), values=data)[0]
        data["count"] = util.safe_int(data["count"])
        return data

    @staticmethod
    def get_image_url(page):
        """Extract url of one manga page"""
        return text.extract(page, '<img id="mainimage" src="', '"')[0]
