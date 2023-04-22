# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vipergirls.to/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vipergirls\.to"


class VipergirlsExtractor(Extractor):
    """Base class for vipergirls extractors"""
    category = "vipergirls"
    root = "https://vipergirls.to"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root

    def items(self):
        for html in self.posts():

            pos = html.find('<a href="')
            if pos < 0:
                continue

            title = text.extr(html, '<h2 class="title', '<')
            data = {
                "title": text.unescape(title.partition(">")[2].strip()),
            }

            yield Message.Directory, data
            for href in text.extract_iter(html, '<a href="', '"', pos):
                yield Message.Queue, href, data


class VipergirlsThreadExtractor(VipergirlsExtractor):
    """Extractor for vipergirls threads"""
    subcategory = "thread"
    pattern = BASE_PATTERN + r"/threads/(\d+)(?:-[^/?#]+)?(/page\d+)?$"
    test = (
        (("https://vipergirls.to/threads/4328304"
          "-2011-05-28-Danica-Simply-Beautiful-x112-4500x3000"), {
            "url": "b22feaa35a358bb36086c2b9353aee28989e1d7a",
            "count": 227,
        }),
        ("https://vipergirls.to/threads/6858916-Karina/page4", {
            "count": 1294,
        }),
        ("https://vipergirls.to/threads/4328304"),
    )

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.page = match.groups()

    def posts(self):
        url = "{}/threads/{}{}".format(
            self.root, self.thread_id, self.page or "")

        while True:
            page = self.request(url).text
            yield from text.extract_iter(
                page, '<div class="postbody">', '</blockquote>')

            url = text.extr(page, '<a rel="next" href="', '"')
            if not url:
                return
            url = "{}/{}".format(self.root, url)


class VipergirlsPostExtractor(VipergirlsExtractor):
    """Extractor for vipergirls posts"""
    subcategory = "post"
    pattern = (BASE_PATTERN +
               r"/threads/(\d+)(?:-[^/?#]+)?\?(p=\d+[^#]*)#post(\d+)")
    test = (
        (("https://vipergirls.to/threads/4328304-2011-05-28-Danica-Simply-"
          "Beautiful-x112-4500x3000?p=116038081&viewfull=1#post116038081"), {
            "pattern": r"https://vipr\.im/\w{12}$",
            "range": "2-113",
            "count": 112,
            "keyword": {
                "title": "FemJoy Danica - Simply Beautiful (x112) 3000x4500",
            },
        }),
    )

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.query, self.post_id = match.groups()

    def posts(self):
        url = "{}/threads/{}?{}".format(self.root, self.thread_id, self.query)
        page = self.request(url).text

        try:
            pos = page.index('id="post_' + self.post_id + '"')
            return (text.extract(
                page, '<div class="postbody">', '</blockquote>', pos)[0],)
        except Exception:
            raise exception.NotFoundError("post")
