# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
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
    pattern = [r"(?:https?://)?(?:www\.)?readcomiconline\.to/Comic/[^/]+/?$"]
    test = [("http://readcomiconline.to/Comic/W-i-t-c-h", {
        "url": "c5a530538a30b176916e30cbe223a93d83cb2691",
    })]

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        return reversed(list(
            text.extract_iter(page, '                <li><a href="', '"')
        ))


class ReadcomiconlineIssueExtractor(ReadcomiconlineExtractor,
                                    kissmanga.KissmangaChapterExtractor):
    """Extractor for comic-issues from readcomiconline.to"""
    subcategory = "issue"
    pattern = [r"(?:https?://)?(?:www\.)?readcomiconline\.to/"
               r"Comic/.+/.+\?id=\d+"]
    test = [("http://readcomiconline.to/Comic/W-i-t-c-h/Issue-130?id=22289", {
        "url": "dd1659d9eb5f6ebb421e66316c98d71682a44c2d",
        "keyword": "bc2f937893c1204ba40e0293e86f0a8943be1304",
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
