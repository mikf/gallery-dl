# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://8kun.top/"""

from .common import Extractor, Message
from .. import text


class _8kunThreadExtractor(Extractor):
    """Extractor for 8kun threads"""
    category = "8kun"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?8kun\.top/([^/]+)/res/(\d+)"
    test = (
        ("https://8kun.top/test/res/65248.html", {
            "pattern": r"https://media\.8kun\.top/file_store/\w{64}\.\w+",
            "count": ">= 8",
        }),
        # old-style file URLs (#1101)
        ("https://8kun.top/d/res/13258.html", {
            "pattern": r"https://media\.8kun\.top/d/src/\d+(-\d)?\.\w+",
            "range": "1-20",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://8kun.top/{}/res/{}.json".format(self.board, self.thread)
        posts = self.request(url).json()["posts"]
        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])
        process = self._process

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Version, 1
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
        url = ("https://media.8kun.top/" +
               ("file_store/" if len(tim) > 16 else post["board"] + "/src/") +
               tim + post["ext"])
        return Message.Url, url, post


class _8kunBoardExtractor(Extractor):
    """Extractor for 8kun boards"""
    category = "8kun"
    subcategory = "board"
    pattern = r"(?:https?://)?8kun\.top/([^/?#]+)/(?:index|\d+)\.html"
    test = (
        ("https://8kun.top/v/index.html", {
            "pattern": _8kunThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://8kun.top/v/2.html"),
        ("https://8kun.top/v/index.html?PageSpeed=noscript"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def items(self):
        url = "https://8kun.top/{}/threads.json".format(self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "https://8kun.top/{}/res/{}.html".format(
                    self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = _8kunThreadExtractor
                yield Message.Queue, url, thread
