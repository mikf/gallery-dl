# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://wikieat.club/"""

from .common import Extractor, Message
from .. import text


class WikieatThreadExtractor(Extractor):
    """Extractor for Wikieat threads"""
    category = "wikieat"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?wikieat\.club/([^/]+)/res/(\d+)"
    test = ("https://wikieat.club/cel/res/25321.html", {
        "pattern": r"https://wikieat\.club/cel/src/\d+(-\d)?\.\w+",
        "count": ">= 200",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://wikieat.club/{}/res/{}.json".format(
            self.board, self.thread)
        posts = self.request(url).json()["posts"]
        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])
        process = self._process

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Directory, data
        for post in posts:
            if "filename" in post:
                yield process(post, data)
                if "extra_files" in post:
                    for post["num"], filedata in enumerate(
                            post["extra_files"], 1):
                        yield process(post, filedata)

    @staticmethod
    def _process(post, data):
        post.update(data)
        post["extension"] = post["ext"][1:]
        tim = post["tim"]
        url = ("https://wikieat.club/" +
               post["board"] + "/src/" +
               tim + post["ext"])
        return Message.Url, url, post


class WikieatBoardExtractor(Extractor):
    """Extractor for Wikieat boards"""
    category = "wikieat"
    subcategory = "board"
    pattern = (r"(?:https?://)?wikieat\.club"
               r"/([^/?#]+)/(?:index|catalog|\d+)\.html")
    test = (
        ("https://wikieat.club/cel/index.html", {
            "pattern": WikieatThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://wikieat.club/cel/catalog.html"),
        ("https://wikieat.club/cel/2.html")
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def items(self):
        url = "https://wikieat.club/{}/threads.json".format(self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "https://wikieat.club/{}/res/{}.html".format(
                    self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = WikieatThreadExtractor
                yield Message.Queue, url, thread
