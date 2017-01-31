# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic-issues and entire comics from http://kisscomic.us/"""

from . import kissmanga
from .. import text


class KisscomicExtractor(kissmanga.KissmangaExtractor):
    """Base class for kisscomic extractors"""
    category = "kisscomic"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    root = "http://kisscomic.us"


class KisscomicComicExtractor(KisscomicExtractor,
                              kissmanga.KissmangaMangaExtractor):
    """Extractor for comics from kisscomic.us"""
    subcategory = "comic"
    pattern = [r"(?:https?://)?(?:www\.)?kisscomic\.us/comics/[^/]+\.html$"]
    test = [("http://kisscomic.us/comics/47-ronin.html", {
        "url": "8c180e2ec2492712b089ca091c54909cb0fe3d4a",
    })]

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        pos = page.find('<div class="list-chapter mCustomScrollbar">')
        return reversed(list(
            text.extract_iter(page, '<li><a href="', '"', pos)
        ))


class KisscomicIssueExtractor(KisscomicExtractor,
                              kissmanga.KissmangaChapterExtractor):
    """Extractor for comic-issues from kisscomic.us"""
    subcategory = "issue"
    pattern = [r"(?:https?://)?(?:www\.)?kisscomic\.us/"
               r"chapters/.+-chapter-\d+\.html"]
    test = [("http://kisscomic.us/chapters/47-ronin-chapter-4.html", {
        "url": "7f8e40bf04c4b36f14a60a8e45692068a9a1f88e",
        "keyword": "a685f92b6989eebf57f8981b1edd6d3de9148ad6",
    })]

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        info = text.extract(page, "<title>", " Comic - Read ")[0]
        comic, issue = info.rsplit(" ", maxsplit=1)
        return {
            "comic": comic,
            "issue": issue,
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract list of all image-urls for a comic issue"""
        return list(text.extract_iter(page, '<li><img src="', '"'))
