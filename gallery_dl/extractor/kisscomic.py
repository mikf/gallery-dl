# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract comic-issues and entire comics from http://kisscomic.us/"""

from .common import Extractor, Message
from .. import text, cloudflare, cache
import re

class KisscomicExtractor(Extractor):
    """Base class for kisscomic extractors"""
    category = "kisscomic"
    directory_fmt = ["{category}", "{comic}", "{issue:>03}"]
    filename_fmt = "{comic}_{issue:>03}_{page:>03}.{extension}"
    url_base = "http://kisscomic.us"

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)
        self.session.headers["Referer"] = self.url_base
        self.cookies = cache.cache(maxage=365*24*60*60, keyarg=0)(_cache_helper)

    def request(self, url, cookies=None):
        cookies = self.cookies(self.url_base, cookies)
        if cookies:
            self.session.cookies = cookies
        response = self.session.get(url)
        if response.status_code != 200:
            self.cookies.invalidate(self.url_base)
            cookies = cloudflare.solve_challenge(self.session, self.url_base)
            response = self.request(url, cookies)
        return response


class KisscomicMangaExtractor(KisscomicExtractor):
    """Extractor for comics from kisscomic.us"""
    subcategory = "comic"
    pattern = [r"(?:https?://)?(?:www\.)?kisscomic\.us/comics/[^/]+\.html$"]
    test = [("http://kisscomic.us/comics/47-ronin.html", {
        "url": "8c180e2ec2492712b089ca091c54909cb0fe3d4a",
    })]

    def items(self):
        yield Message.Version, 1
        for chapter in self.get_chapters():
            yield Message.Queue, self.url_base + chapter

    def get_chapters(self):
        """Return a list of all chapter urls"""
        page = self.request(self.url).text
        pos = page.find('<div class="list-chapter mCustomScrollbar">')
        return reversed(list(
            text.extract_iter(page, '<li><a href="', '"', pos)
        ))


class KisscomicIssueExtractor(KisscomicExtractor):
    """Extractor for comic-issues from kisscomic.us"""
    subcategory = "issue"
    pattern = [r"(?:https?://)?(?:www\.)?kisscomic\.us/chapters/.+-chapter-\d+\.html"]
    test = [("http://kisscomic.us/chapters/47-ronin-chapter-4.html", {
        "url": "7f8e40bf04c4b36f14a60a8e45692068a9a1f88e",
        "keyword": "a685f92b6989eebf57f8981b1edd6d3de9148ad6",
    })]

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["page"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

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
        """Extract list of all image-urls for a manga chapter"""
        return list(text.extract_iter(page, '<li><img src="', '"'))


def _cache_helper(key, item=None):
    return item
