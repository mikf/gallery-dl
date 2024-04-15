# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://readcomiconline.li/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import binascii
import re

BASE_PATTERN = r"(?i)(?:https?://)?(?:www\.)?readcomiconline\.(?:li|to)"


class ReadcomiconlineBase():
    """Base class for readcomiconline extractors"""
    category = "readcomiconline"
    directory_fmt = ("{category}", "{comic}", "{issue:>03}")
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    archive_fmt = "{issue_id}_{page}"
    root = "https://readcomiconline.li"
    request_interval = (3.0, 6.0)

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
                self.input()
            else:
                raise exception.StopExtraction(
                    "Redirect to \n%s\nVisit this URL in your browser and "
                    "solve the CAPTCHA to continue", response.url)


class ReadcomiconlineIssueExtractor(ReadcomiconlineBase, ChapterExtractor):
    """Extractor for comic-issues from readcomiconline.li"""
    subcategory = "issue"
    pattern = BASE_PATTERN + r"(/Comic/[^/?#]+/[^/?#]+\?)([^#]+)"
    example = "https://readcomiconline.li/Comic/TITLE/Issue-123?id=12345"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match)
        self.params = match.group(2)

    def _init(self):
        params = text.parse_query(self.params)
        quality = self.config("quality")

        if quality is None or quality == "auto":
            if "quality" not in params:
                params["quality"] = "hq"
        else:
            params["quality"] = str(quality)

        self.gallery_url += "&".join(k + "=" + v for k, v in params.items())
        self.issue_id = params.get("id")

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
            (beau(url), None)
            for url in text.extract_iter(
                page, "lstImages.push('", "'",
            )
        ]


class ReadcomiconlineComicExtractor(ReadcomiconlineBase, MangaExtractor):
    """Extractor for comics from readcomiconline.li"""
    chapterclass = ReadcomiconlineIssueExtractor
    subcategory = "comic"
    pattern = BASE_PATTERN + r"(/Comic/[^/?#]+/?)$"
    example = "https://readcomiconline.li/Comic/TITLE"

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


def beau(url):
    """https://readcomiconline.li/Scripts/rguard.min.js"""
    url = url.replace("_x236", "d")
    url = url.replace("_x945", "g")

    if url.startswith("https"):
        return url

    url, sep, rest = url.partition("?")
    containsS0 = "=s0" in url
    url = url[:-3 if containsS0 else -6]
    url = url[4:22] + url[25:]
    url = url[0:-6] + url[-2:]
    url = binascii.a2b_base64(url).decode()
    url = url[0:13] + url[17:]
    url = url[0:-2] + ("=s0" if containsS0 else "=s1600")
    return "https://2.bp.blogspot.com/" + url + sep + rest
