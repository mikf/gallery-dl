# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://readcomiconline.to/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import re


class ReadcomiconlineBase():
    """Base class for readcomiconline extractors"""
    category = "readcomiconline"
    directory_fmt = ("{category}", "{comic}", "{issue:>03}")
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    archive_fmt = "{issue_id}_{page}"
    root = "https://readcomiconline.to"

    def request(self, url, **kwargs):
        """Detect and handle redirects to CAPTCHA pages"""
        while True:
            response = Extractor.request(self, url, **kwargs)
            if not response.history or "/AreYouHuman" not in response.url:
                return response
            if self.config("captcha", "stop") == "wait":
                self.log.warning(
                    "Redirect to \n%s\nVisit this URL in your browser, solve "
                    "the CAPTCHA, and press ENTER to continue", response.url)
                try:
                    input()
                except (EOFError, OSError):
                    pass
            else:
                raise exception.StopExtraction(
                    "Redirect to \n%s\nVisit this URL in your browser and "
                    "solve the CAPTCHA to continue", response.url)


class ReadcomiconlineIssueExtractor(ReadcomiconlineBase, ChapterExtractor):
    """Extractor for comic-issues from readcomiconline.to"""
    subcategory = "issue"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.to"
               r"(/Comic/[^/?&#]+/[^/?&#]+\?id=(\d+))")
    test = ("https://readcomiconline.to/Comic/W-i-t-c-h/Issue-130?id=22289", {
        "url": "2bbab6ec4fbc05d269cca420a82a9b5acda28682",
        "keyword": "30fe110273e871305001f33c18634516a0a51421",
    })

    def __init__(self, match):
        ChapterExtractor.__init__(self, match)
        self.issue_id = match.group(2)

    def metadata(self, page):
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

    def images(self, page):
        return [
            (url, None)
            for url in text.extract_iter(
                page, 'lstImages.push("', '"'
            )
        ]


class ReadcomiconlineComicExtractor(ReadcomiconlineBase, MangaExtractor):
    """Extractor for comics from readcomiconline.to"""
    chapterclass = ReadcomiconlineIssueExtractor
    subcategory = "comic"
    pattern = (r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.to"
               r"(/Comic/[^/?&#]+/?)$")
    test = (
        ("https://readcomiconline.to/Comic/W-i-t-c-h", {
            "url": "e231bc2a293edb465133c37a8e36a7e7d94cab14",
            "keyword": "3986248e4458fa44a201ec073c3684917f48ee0c",
        }),
        ("https://readcomiconline.to/Comic/Bazooka-Jules", {
            "url": "711674cb78ed10bd2557315f7a67552d01b33985",
            "keyword": "f5ba5246cd787bb750924d9690cb1549199bd516",
        }),
    )

    def chapters(self, page):
        results = []
        comic, pos = text.extract(page, ' class="barTitle">', '<')
        page , pos = text.extract(page, ' class="listing">', '</table>', pos)

        comic = comic.rpartition("information")[0].strip()
        needle = ' title="Read {} '.format(comic)
        comic = text.unescape(comic)

        for item in text.extract_iter(page, ' href="', ' comic online '):
            url, _, issue = item.partition(needle)
            url = url.rpartition('"')[0]
            if issue.startswith('Issue #'):
                issue = issue[7:]
            results.append((self.root + url, {
                "comic": comic, "issue": issue,
                "issue_id": text.parse_int(url.rpartition("=")[2]),
                "lang": "en", "language": "English",
            }))
        return results
