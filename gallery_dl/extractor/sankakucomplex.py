# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.sankakucomplex.com/"""

from .common import Extractor, Message
from .. import text, util
import re


class SankakucomplexExtractor(Extractor):
    """Base class for sankakucomplex extractors"""
    category = "sankakucomplex"
    root = "https://www.sankakucomplex.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path = match.group(1)


class SankakucomplexArticleExtractor(SankakucomplexExtractor):
    """Extractor for articles on www.sankakucomplex.com"""
    subcategory = "article"
    directory_fmt = ("{category}", "{date:%Y-%m-%d} {title}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{date:%Y%m%d}_{filename}"
    pattern = (r"(?:https?://)?www\.sankakucomplex\.com"
               r"/(\d{4}/\d\d/\d\d/[^/?#]+)")
    test = (
        ("https://www.sankakucomplex.com/2019/05/11/twitter-cosplayers", {
            "url": "4a9ecc5ae917fbce469280da5b6a482510cae84d",
            "keyword": "bfe08310e7d9a572f568f6900e0ed0eb295aa2b3",
        }),
        ("https://www.sankakucomplex.com/2009/12/01/sexy-goddesses-of-2ch", {
            "url": "a1e249173fd6c899a8134fcfbd9c925588a63f7c",
            "keyword": "e78fcc23c2711befc0969a45ea5082a29efccf68",
        }),
        # videos (#308)
        (("https://www.sankakucomplex.com/2019/06/11"
          "/darling-ol-goddess-shows-off-her-plump-lower-area/"), {
            "pattern": r"/wp-content/uploads/2019/06/[^/]+\d\.mp4",
            "range": "26-",
            "count": 5,
        }),
        # youtube embeds (#308)
        (("https://www.sankakucomplex.com/2015/02/12"
          "/snow-miku-2015-live-magical-indeed/"), {
            "options": (("embeds", True),),
            "pattern": r"https://www.youtube.com/embed/",
            "range": "2-",
            "count": 2,
        }),
    )

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
    pattern = (r"(?:https?://)?www\.sankakucomplex\.com"
               r"/((?:tag|category|author)/[^/&?#]+)")
    test = (
        ("https://www.sankakucomplex.com/tag/cosplay/", {
            "range": "1-50",
            "count": 50,
            "pattern": SankakucomplexArticleExtractor.pattern,
        }),
        ("https://www.sankakucomplex.com/category/anime/"),
        ("https://www.sankakucomplex.com/author/rift/page/5/"),
    )

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
