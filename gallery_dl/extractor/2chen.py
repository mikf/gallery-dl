# -*- coding: utf-8 -*-

# Copyright 2017-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from .common import Extractor, Message
from .. import text


class _2chenThreadExtractor(Extractor):
    """Extractor for 2chen threads"""
    category = "2chen"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{filename}"
    pattern = (r"(?:https?://)?2chen\.moe"
               r"/([^/]+)/(\d+)")
    test = ("https://2chen.moe/jp/303786",)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://2chen.moe/{}/{}".format(self.board, self.thread)
        page = self.request(url, encoding="utf-8").text
        data = self.metadata(page)
        yield Message.Directory, data
        for post in self.posts(page):
            if post["url"] is None or post["filename"] is None:
                continue
            url = "https://2chen.moe{}".format(post["url"])
            yield Message.Url, url, post

    def metadata(self, page):
        title = text.extract(page, "<h3>", "</h3>")[0]
        return {
            "board": self.board,
            "thread": self.thread,
            "title": title
        }

    def posts(self, page):
        posts = text.extract_iter(
            page, '<figcaption class="spaced">', '</figcaption>')
        return [self.parse(post) for post in posts]

    def parse(self, post):
        data = self._extract_post(post)
        data["extension"] = str(data["filename"]).split(".")[-1]
        return data

    @staticmethod
    def _extract_post(post):
        return text.extract_all(post, (
            ('url', '</span><a href="', '" download="'),
            ('filename', '', '" data-hash=')
        ))[0]


class _2chenBoardExtractor(Extractor):
    """Extractor for 2chen boards"""
    category = "2chen"
    subcategory = "board"
    pattern = r"(?:https?://)?2chen\.moe/([^/?#]+)/?(?:catalog)?$"
    test = (
        ("https://2chen.moe/co/", {
            "pattern": _2chenThreadExtractor.pattern
        }),
        ("https://2chen.moe/co", {
            "pattern": _2chenThreadExtractor.pattern
        }),
        ("https://2chen.moe/co/catalog", {
            "pattern": _2chenThreadExtractor.pattern
        }))

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group()

    def items(self):
        url = "https://2chen.moe/{}/catalog".format(self.board)
        page = self.request(url).text
        data = {"_extractor": _2chenThreadExtractor}
        for thread in self.threads(page):
            url = "https://2chen.moe{}".format(thread)
            yield Message.Queue, url, data

    def threads(self, page):
        return text.extract_iter(page, '<figure><a href="', '">')
