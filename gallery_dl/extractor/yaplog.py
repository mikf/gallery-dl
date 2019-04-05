# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yaplog.jp/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, util


class YaplogExtractor(AsynchronousMixin, Extractor):
    """Base class for yaplog extractors"""
    category = "yaplog"
    root = "https://yaplog.jp"
    filename_fmt = "{post_id}_{image_id}_{title}.{extension}"
    directory_fmt = ("{category}", "{user}")
    archive_fmt = "{user}_{image_id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        yield Message.Version, 1
        for urls, data in self.posts():
            yield Message.Directory, data
            for num, url in enumerate(urls, 1):
                page = self.request(url).text if num > 1 else url
                iurl = text.extract(page, '<img src="', '"')[0]
                iid, _, ext = iurl.rpartition("/")[2].rpartition(".")
                image = {
                    "url"      : iurl,
                    "num"      : num,
                    "image_id" : text.parse_int(iid.partition("_")[0]),
                    "extension": ext,
                }
                image.update(data)
                yield Message.Url, iurl, image

    def posts(self):
        """Return an iterable with (data, image URLs) tuples"""

    def _parse_post(self, url):
        page = self.request(url).text
        title, pos = text.extract(page, 'class="title">', '<')
        date , pos = text.extract(page, 'class="date">' , '<', pos)
        pid  , pos = text.extract(page, '/archive/'     , '"', pos)
        prev , pos = text.extract(page, 'class="last"><a href="', '"', pos)

        urls = list(text.extract_iter(page, '<li><a href="', '"', pos))
        urls[0] = page  # cache HTML of first page

        if len(urls) == 24 and text.extract(page, '(1/', ')')[0] != '24':
            # there are a maximum of 24 image entries in an /image/ page
            # -> search /archive/ page for the rest
            url = "{}/{}/archive/{}".format(self.root, self.user, pid)
            page = self.request(url).text

            base = "{}/{}/image/{}/".format(self.root, self.user, pid)
            for part in util.advance(text.extract_iter(
                    page, base, '"', pos), 24):
                urls.append(base + part)

        return prev, urls, {
            "post_id": text.parse_int(pid),
            "title"  : text.unescape(title[:-3]),
            "user"   : self.user,
            "date"   : date,
        }


class YaplogUserExtractor(YaplogExtractor):
    """Extractor for a user's blog on yaplog.jp"""
    subcategory = "user"
    pattern = r"(?:https?://)?(?:www\.)?yaplog\.jp/(\w+)/?(?:$|[?&#])"
    test = ("https://yaplog.jp/omitakashi3", {
        "pattern": r"https://img.yaplog.jp/img/18/pc/o/m/i/omitakashi3/0/",
        "count": ">= 2",
    })

    def posts(self):
        url = "{}/{}/image/".format(self.root, self.user)
        while url:
            url, images, data = self._parse_post(url)
            yield images, data


class YaplogPostExtractor(YaplogExtractor):
    """Extractor for images from a blog post on yaplog.jp"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?yaplog\.jp"
               r"/(\w+)/(?:archive|image)/(\d+)")
    test = ("https://yaplog.jp/imamiami0726/image/1299", {
        "url": "896cae20fa718735a57e723c48544e830ff31345",
        "keyword": "9bb89e959bb518a8797242aa3e03e17caa00beba",
    })

    def __init__(self, match):
        YaplogExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/{}/image/{}".format(self.root, self.user, self.post_id)
        _, images, data = self._parse_post(url)
        return ((images, data),)
