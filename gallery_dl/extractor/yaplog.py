# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yaplog.jp/"""

from .common import Extractor, Message
from .. import text, util


class YaplogExtractor(Extractor):
    """Base class for yaplog extractors"""
    category = "yaplog"
    root = "https://yaplog.jp"
    filename_fmt = "{post_id}_{image_id}_{title}.{extension}"
    directory_fmt = ("{category}", "{user}")
    archive_fmt = "{post_id}_{image_id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = None

    def items(self):
        yield Message.Version, 1
        for images, data in self.posts():
            yield Message.Directory, data
            for url in images:
                iid, _, ext = url.rpartition("/")[2].rpartition(".")
                image = {
                    "image_id" : text.parse_int(iid.partition("_")[0]),
                    "extension": ext,
                }
                image.update(data)
                yield Message.Url, url, image

    def posts(self):
        """Return an iterable with (data, image URLs) tuples"""

    def _extract_post(self, url):
        page = self.request(url).text
        title, pos = text.extract(page, 'class="title">', '<')
        date , pos = text.extract(page, 'class="date">' , '<', pos)
        post , pos = text.extract(page, '/archive/'     , '"', pos)
        url  , pos = text.extract(page, 'class="last"><a href="', '"', pos)

        return url, self._images_from_post(page), {
            "post_id": text.parse_int(post),
            "title"  : text.unescape(title[:-3]),
            "user"   : self.user,
            "date"   : date,
        }

    def _images_from_post(self, post):
        urls = text.extract_iter(post, '<li><a href="', '"')

        yield text.extract(post, '<img src="', '"')[0]
        for url in util.advance(urls, 1):
            post = self.request(url).text
            yield text.extract(post, '<img src="', '"')[0]


class YaplogUserExtractor(YaplogExtractor):
    """Extractor for all images from a blog on yaplog.jp"""
    subcategory = "user"
    pattern = r"(?:https://)?(?:www\.)?yaplog\.jp/(\w+)/?(?:$|[?&#])"
    test = ("https://yaplog.jp/omitakashi3", {
        "pattern": r"https://img.yaplog.jp/img/18/pc/o/m/i/omitakashi3/0/",
        "count": ">= 2",
    })

    def __init__(self, match):
        YaplogExtractor.__init__(self, match)
        self.user = match.group(1)

    def posts(self):
        url = "{}/{}/image/".format(self.root, self.user)
        while url:
            url, images, data = self._extract_post(url)
            yield images, data


class YaplogPostExtractor(YaplogExtractor):
    """Extractor for images from a single blog post on yaplog.jp"""
    subcategory = "post"
    pattern = (r"(?:https://)?(?:www\.)?yaplog\.jp"
               r"/(\w+)/(?:archive|image)/(\d+)")
    test = ("https://yaplog.jp/imamiami0726/image/1299", {
        "url": "896cae20fa718735a57e723c48544e830ff31345",
        "keyword": "5c700cb6c505d50b6161c9a3559a186d378eabe3",
    })

    def __init__(self, match):
        YaplogExtractor.__init__(self, match)
        self.user, self.post_id = match.groups()

    def posts(self):
        url = "{}/{}/image/{}".format(self.root, self.user, self.post_id)
        _, images, data = self._extract_post(url)
        return ((images, data),)
