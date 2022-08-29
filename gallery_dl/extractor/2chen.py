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
    filename_fmt = "{time} {filename}.{extension}"
    archive_fmt = "{hash}"
    root = "https://2chen.moe"
    pattern = (r"(?:https?://)?2chen\.moe"
               r"/([^/]+)/(\d+)")
    test = (
        ("https://2chen.moe/jp/303786", {
            "count": ">= 10",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "{}/{}/{}".format(self.root, self.board, self.thread)
        page = self.request(url, encoding="utf-8").text
        data = self.metadata(page)
        yield Message.Directory, data
        for post in self.posts(page):
            post.update(data)
            if post["url"] is None or post["filename"] is None:
                continue
            yield Message.Url, post["url"], post

    def metadata(self, page):
        title = text.extract(page, "<h3>", "</h3>")[0]
        return {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title),
        }

    def posts(self, page):
        """Return list containing relevant posts"""
        posts = text.extract_iter(
            page, 'class="glass media', '</article>')
        return [self.parse(post) for post in posts]

    def parse(self, post):
        extr = text.extract_from(post)
        name = extr('<span>', '</span>')
        date = extr('<time', 'time>')
        date = text.parse_datetime(
            text.extract(date, '>', '</')[0],
            "%d %b %Y (%a) %H:%M:%S", utcoffset=-5.5)
        extr = text.extract_from(extr('<a class="quote"', '</figcaption>'))
        data = {
            "name"    : name,
            "date"    : date,
            "time"    : text.parse_int(date.timestamp()),
            "no"      : extr('">', '</a>'),
            "url"     : self.root + extr('</span><a href="', '" download='),
            "filename": extr('"', '" data-hash='),
            "hash"    : extr('"', '">'),
        }
        data["filename"], _, data["extension"] = \
            data["filename"].rpartition(".")
        data["ext"] = "." + data["extension"]
        return data


class _2chenBoardExtractor(Extractor):
    """Extractor for 2chen boards"""
    category = "2chen"
    subcategory = "board"
    root = "https://2chen.moe"
    pattern = r"(?:https?://)?2chen\.moe/([^/?#]+)(?:/catalog)?/?$"
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
        self.board = match.group(1)

    def items(self):
        url = "{}/{}/catalog".format(self.root, self.board)
        page = self.request(url).text
        data = {"_extractor": _2chenThreadExtractor}
        for thread in self.threads(page):
            url = self.root + thread
            yield Message.Queue, url, data

    @staticmethod
    def threads(page):
        return text.extract_iter(page, '<figure><a href="', '">')
