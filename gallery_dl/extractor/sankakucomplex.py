# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://news.sankakucomplex.com/"""

from .common import Extractor, Message
from .. import text, util
import re


class SankakucomplexExtractor(Extractor):
    """Base class for sankakucomplex extractors"""
    category = "sankakucomplex"
    root = "https://news.sankakucomplex.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)


class SankakucomplexArticleExtractor(SankakucomplexExtractor):
    """Extractor for articles on news.sankakucomplex.com"""
    subcategory = "article"
    directory_fmt = ("{category}", "{date:%Y-%m-%d} {title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{date:%Y%m%d}_{filename}"
    pattern = (r"(?:https?://)?(?:news|www)\.sankakucomplex\.com"
               r"/(\d\d\d\d/\d\d/\d\d/[^/?#]+)")
    example = "https://news.sankakucomplex.com/1970/01/01/TITLE"

    def items(self):
        url = "{}/{}/?pg=X".format(self.root, self.path)
        extr = text.extract_from(self.request(url).text)
        data = {
            "title"      : text.unescape(
                extr('property="og:title" content="', '"')),
            "description": text.unescape(
                extr('property="og:description" content="', '"')),
            "date"       : text.parse_datetime(
                extr('property="article:published_time" content="', '"')),
        }
        content = extr('<div class="entry-content">', '</article>')
        data["tags"] = text.split_html(extr('="meta-tags">', '</div>'))[::2]

        files = self._extract_images(content)
        if self.config("videos", True):
            files += self._extract_videos(content)
        if self.config("embeds", False):
            files += self._extract_embeds(content)
        data["count"] = len(files)

        yield Message.Directory, data
        for num, url in enumerate(files, 1):
            file = text.nameext_from_url(url)
            if url[0] == "/":
                url = text.urljoin(self.root, url)
            file["url"] = url
            file["num"] = num
            file.update(data)
            yield Message.Url, url, file

    @staticmethod
    def _extract_images(content):
        orig_sub = re.compile(r"-\d+x\d+\.").sub
        return [
            orig_sub(".", url) for url in
            util.unique(text.extract_iter(content, 'data-lazy-src="', '"'))
        ]

    @staticmethod
    def _extract_videos(content):
        return re.findall(r"<source [^>]*src=[\"']([^\"']+)", content)

    @staticmethod
    def _extract_embeds(content):
        return [
            "ytdl:" + url for url in
            re.findall(r"<iframe [^>]*src=[\"']([^\"']+)", content)
        ]


class SankakucomplexTagExtractor(SankakucomplexExtractor):
    """Extractor for sankakucomplex blog articles by tag or author"""
    subcategory = "tag"
    pattern = (r"(?:https?://)?(?:news|www)\.sankakucomplex\.com"
               r"/((?:tag|category|author)/[^/?#]+)")
    example = "https://news.sankakucomplex.com/tag/TAG/"

    def items(self):
        pnum = 1
        data = {"_extractor": SankakucomplexArticleExtractor}

        while True:
            url = "{}/{}/page/{}/".format(self.root, self.path, pnum)
            response = self.request(url, fatal=False)
            if response.status_code >= 400:
                return
            for url in util.unique_sequence(text.extract_iter(
                    response.text, 'data-direct="', '"')):
                yield Message.Queue, url, data
            pnum += 1
