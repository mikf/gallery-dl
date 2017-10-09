# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic-issues and entire comics from http://readcomiconline.to/"""

from . import kissmanga
from .. import text
import re


class ReadcomiconlineExtractor(kissmanga.KissmangaExtractor):
    """Base class for readcomiconline extractors"""
    category = "readcomiconline"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    root = "http://readcomiconline.to"


class ReadcomiconlineComicExtractor(ReadcomiconlineExtractor,
                                    kissmanga.KissmangaMangaExtractor):
    """Extractor for comics from readcomiconline.to"""
    subcategory = "comic"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.to/"
               r"Comic/[^/?&#]+/?$"]
    test = [
        ("http://readcomiconline.to/Comic/W-i-t-c-h", {
            "url": "c5a530538a30b176916e30cbe223a93d83cb2691",
            "keyword": "51097f2b65da683160dbea4de128dbec1cbf9357",
        }),
        ("http://readcomiconline.to/Comic/Bazooka-Jules", {
            "url": "e517dca61dff489f18ca781084f59a9eeb60a6b6",
            "keyword": "7d4877d1215650a768097a8626a2f0c6083119a4",
        }),
    ]

    def chapters(self, page):
        results = []
        comic, pos = text.extract(page, '<div class="heading"><h3>', '<')
        page , pos = text.extract(page, '<ul class="list">', '</ul>', pos)

        for item in text.extract_iter(page, '<a href="', '</span>'):
            url, _, issue = item.partition('"><span>')
            if issue.startswith('Issue #'):
                issue = issue[7:]
            results.append((self.root + url, {
                "comic": comic, "issue": issue, "id": url.rpartition("=")[2],
                "lang": "en", "language": "English",
            }))
        return results


class ReadcomiconlineIssueExtractor(ReadcomiconlineExtractor,
                                    kissmanga.KissmangaChapterExtractor):
    """Extractor for comic-issues from readcomiconline.to"""
    subcategory = "issue"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.to/"
               r"Comic/[^/?&#]+/[^/?&#]+\?id=\d+"]
    test = [("http://readcomiconline.to/Comic/W-i-t-c-h/Issue-130?id=22289", {
        "url": "a45c77f8fbde66091fe2346d6341f9cf3c6b1bc5",
        "keyword": "dee8a8a44659825afe1d69e1d809a48b03e98c68",
    })]

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        comic, pos = text.extract(page, "   - Read\r\n    ", "\r\n")
        iinfo, pos = text.extract(page, "    ", "\r\n", pos)
        match = re.match(r"(?:Issue )?#(\d+)|(.+)", iinfo)
        return {
            "comic": comic,
            "issue": match.group(1) or match.group(2),
            "lang": "en",
            "language": "English",
        }

    @staticmethod
    def get_image_urls(page):
        """Extract list of all image-urls for a manga chapter"""
        return list(text.extract_iter(page, 'lstImages.push("', '"'))
