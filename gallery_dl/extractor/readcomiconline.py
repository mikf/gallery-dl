# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic-issues and entire comics from http://readcomiconline.to/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, cloudflare
import re


class ReadcomiconlineBase():
    """Base class for readcomiconline extractors"""
    category = "readcomiconline"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    archive_fmt = "{issue_id}_{page}"
    root = "http://readcomiconline.to"
    useragent = "Wget/1.19.2 (linux-gnu)"

    request = cloudflare.request_func


class ReadcomiconlineComicExtractor(ReadcomiconlineBase, MangaExtractor):
    """Extractor for comics from readcomiconline.to"""
    subcategory = "comic"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?(readcomiconline\.to"
               r"/Comic/[^/?&#]+/?)$"]
    test = [
        ("http://readcomiconline.to/Comic/W-i-t-c-h", {
            "url": "c5a530538a30b176916e30cbe223a93d83cb2691",
            "keyword": "3986248e4458fa44a201ec073c3684917f48ee0c",
        }),
        ("http://readcomiconline.to/Comic/Bazooka-Jules", {
            "url": "e517dca61dff489f18ca781084f59a9eeb60a6b6",
            "keyword": "f5ba5246cd787bb750924d9690cb1549199bd516",
        }),
    ]

    def __init__(self, match):
        MangaExtractor.__init__(self, match)
        self.session.headers["User-Agent"] = self.useragent

    def chapters(self, page):
        results = []
        comic, pos = text.extract(page, '<div class="heading"><h3>', '<')
        page , pos = text.extract(page, '<ul class="list">', '</ul>', pos)

        for item in text.extract_iter(page, '<a href="', '</span>'):
            url, _, issue = item.partition('"><span>')
            if issue.startswith('Issue #'):
                issue = issue[7:]
            results.append((self.root + url, {
                "comic": comic, "issue": issue,
                "issue_id": text.parse_int(url.rpartition("=")[2]),
                "lang": "en", "language": "English",
            }))
        return results


class ReadcomiconlineIssueExtractor(ReadcomiconlineBase, ChapterExtractor):
    """Extractor for comic-issues from readcomiconline.to"""
    subcategory = "issue"
    pattern = [r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.to"
               r"/Comic/[^/?&#]+/[^/?&#]+\?id=(\d+)"]
    test = [("http://readcomiconline.to/Comic/W-i-t-c-h/Issue-130?id=22289", {
        "url": "2bbab6ec4fbc05d269cca420a82a9b5acda28682",
        "keyword": "c6de1c9c8a307dc4be56783c4ac6f1338ffac6fc",
    })]

    def __init__(self, match):
        ChapterExtractor.__init__(self, match.group(0))
        self.issue_id = match.group(1)
        self.session.headers["User-Agent"] = self.useragent

    def get_metadata(self, page):
        comic, pos = text.extract(page, "   - Read\r\n    ", "\r\n")
        iinfo, pos = text.extract(page, "    ", "\r\n", pos)
        match = re.match(r"(?:Issue )?#(\d+)|(.+)", iinfo)
        return {
            "comic": comic,
            "issue": match.group(1) or match.group(2),
            "issue_id": text.parse_int(self.issue_id),
            "lang": "en",
            "language": "English",
        }

    def get_images(self, page):
        self.session.headers["Referer"] = None
        return [
            (url, None)
            for url in text.extract_iter(
                page, 'lstImages.push("', '"'
            )
        ]
