# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.thespectrum.net/manga_scans/"""

from .common import ChapterExtractor, MangaExtractor
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


class SpectrumnexusChapterExtractor(ChapterExtractor):
    """Extractor for manga-chapters or -volumes from thespectrum.net"""
    category = "spectrumnexus"
    directory_fmt = ["{category}", "{manga}", "{chapter_string}"]
    filename_fmt = "{manga}_{chapter_string}_{page:>03}.{extension}"
    archive_fmt = "{manga}_{chapter_string}_{page}"
    pattern = [r"(?:https?://)?view\.thespectrum\.net/series/"
               r"([^\.]+\.html)\?ch=(Chapter\+(\d+)|Volume\+(\d+))"]
    test = [(("http://view.thespectrum.net/series/"
              "toriko.html?ch=Chapter+343&page=1"), {
        "url": "c0fc7dc594841217cc622a67edd79f06e9900333",
        "keyword": "a8abe126cbc5fc798148b0b155242a470c1ba9d1",
    })]

    def __init__(self, match):
        path, self.chapter_string, self.chapter, self.volume = match.groups()
        url = "http://view.thespectrum.net/series/{}?ch={}".format(
            path, self.chapter_string)
        ChapterExtractor.__init__(self, url)

    def get_metadata(self, page):
        data = {
            "chapter": util.safe_int(self.chapter),
            "chapter_string": self.chapter_string.replace("+", " "),
            "volume": util.safe_int(self.volume),
        }
        data = text.extract_all(page, (
            ('manga', '<title>', ' &#183; SPECTRUM NEXUS </title>'),
            ('count', '<div class="viewerLabel"> of ', '<'),
        ), values=data)[0]
        data["count"] = util.safe_int(data["count"])
        return data

    def get_images(self, page):
        params = {"page": 1}
        while True:
            yield text.extract(page, '<img id="mainimage" src="', '"')[0], None
            params["page"] += 1
            page = self.request(self.url, params=params).text
