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
            "keyword": "35cd2a0aba712d6b0e27a9fa2a5e823199d10ca0",
        }),
        ("https://www.sankakucomplex.com/2009/12/01/sexy-goddesses-of-2ch", {
            "url": "a1e249173fd6c899a8134fcfbd9c925588a63f7c",
            "keyword": "8bf60e62fb5e9f2caabb29c16ed58d7e0dcf247f",
        }),
    )

    def items(self):
        url = "{}/{}/?pg=X".format(self.root, self.path)
        extr = text.extract_from(self.request(url).text)
        data = {
            "title"      : text.unescape(
                extr('"og:title" content="', '"')),
            "description": text.unescape(
                extr('"og:description" content="', '"')),
            "date"       : text.parse_datetime(
                extr('"og:updated_time" content="', '"')),
        }
        imgs = self.images(extr)
        data["count"] = len(imgs)
        data["tags"] = text.split_html(extr('="meta-tags">', '</div>'))[::2]

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
