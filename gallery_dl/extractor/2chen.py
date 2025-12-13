# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for 2chen boards"""

from .common import BaseExtractor, Message
from .. import text


class _2chenExtractor(BaseExtractor):
    basecategory = "2chen"


BASE_PATTERN = _2chenExtractor.update({
    "sturdychan": {
        "root": "https://sturdychan.help",
        "pattern": r"(?:sturdychan\.help|2chen\.(?:moe|club))",
    },
    "schan": {
        "root": "https://schan.help/",
        "pattern": r"schan\.help",
    },
})


class _2chenThreadExtractor(_2chenExtractor):
    """Extractor for 2chen threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{no}_{time}"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/(\d+)"
    example = "https://sturdychan.help/a/12345/"

    def items(self):
        board = self.groups[-2]
        thread = self.kwdict["thread"] = self.groups[-1]
        url = f"{self.root}/{board}/{thread}"
        page = self.request(url, encoding="utf-8", notfound="thread").text

        self.kwdict["board"], pos = text.extract(
            page, 'class="board">/', '/<')
        self.kwdict["title"] = text.unescape(text.extract(
            page, "<h3>", "</h3>", pos)[0])

        yield Message.Directory, "", {}
        for post in self.posts(page):
            url = post["url"]
            if not url:
                continue
            if url[0] == "/":
                url = self.root + url
            post["url"] = url = url.partition("?")[0]

            post["time"] = text.parse_int(post["date"].timestamp())
            yield Message.Url, url, text.nameext_from_url(
                post["filename"], post)

    def posts(self, page):
        """Return iterable with relevant posts"""
        return map(self.parse, text.extract_iter(
            page, 'class="glass media', '</article>'))

    def parse(self, post):
        extr = text.extract_from(post)
        return {
            "name"    : text.unescape(extr("<span>", "</span>")),
            "date"    : self.parse_datetime(
                extr("<time", "<").partition(">")[2],
                "%d %b %Y (%a) %H:%M:%S"
            ),
            "no"      : extr('href="#p', '"'),
            "filename": text.unescape(extr('download="', '"')),
            "url"     : text.extr(extr("<figure>", "</"), 'href="', '"'),
            "hash"    : extr('data-hash="', '"'),
        }


class _2chenBoardExtractor(_2chenExtractor):
    """Extractor for 2chen boards"""
    subcategory = "board"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)(?:/catalog|/?$)"
    example = "https://sturdychan.help/a/"

    def items(self):
        url = f"{self.root}/{self.groups[-1]}/catalog"
        page = self.request(url, notfound="board").text
        data = {"_extractor": _2chenThreadExtractor}
        for thread in text.extract_iter(
                page, '<figure><a href="', '"'):
            yield Message.Queue, self.root + thread, data
