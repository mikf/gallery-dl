# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.sankakucomplex.com/"""

from .common import Extractor, Message
from .. import text
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
               r"/(\d{4}/\d\d/\d\d/[^/?&#]+)")
    test = (
        ("https://www.sankakucomplex.com/2019/05/11/twitter-cosplayers", {
            "url": "4a9ecc5ae917fbce469280da5b6a482510cae84d",
            "keyword": "bfe08310e7d9a572f568f6900e0ed0eb295aa2b3",
        }),
        ("https://www.sankakucomplex.com/2009/12/01/sexy-goddesses-of-2ch", {
            "url": "a1e249173fd6c899a8134fcfbd9c925588a63f7c",
            "keyword": "e78fcc23c2711befc0969a45ea5082a29efccf68",
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
        imgs = self.images(extr)
        data["count"] = len(imgs)
        data["tags"] = text.split_html(extr('="meta-tags">', '</div>'))[::2]

        yield Message.Version, 1
        yield Message.Directory, data
        for img in imgs:
            img.update(data)
            yield Message.Url, img["url"], img

    def images(self, extr):
        num = 0
        imgs = []
        urls = set()
        orig = re.compile(r"-\d+x\d+\.")

        extr('<div class="entry-content">', '')
        while True:
            url = extr('data-lazy-src="', '"')
            if not url:
                return imgs
            if url in urls:
                continue
            if url[0] == "/":
                url = text.urljoin(self.root, url)
            url = orig.sub(".", url)
            num += 1
            imgs.append(text.nameext_from_url(url, {
                "url"   : url,
                "num"   : num,
            }))
            urls.add(url)


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
        last = None
        data = {"_extractor": SankakucomplexArticleExtractor}

        yield Message.Version, 1
        while True:
            url = "{}/{}/page/{}/".format(self.root, self.path, pnum)
            response = self.request(url, fatal=False)
            if response.status_code >= 400:
                return
            for url in text.extract_iter(response.text, 'data-direct="', '"'):
                if url != last:
                    last = url
                    yield Message.Queue, url, data
            pnum += 1
