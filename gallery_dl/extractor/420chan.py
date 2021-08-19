# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://420chan.org/"""

from .common import Extractor, Message


class _420chanThreadExtractor(Extractor):
    """Extractor for 420chan threads"""
    category = "420chan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    archive_fmt = "{board}_{thread}_{filename}"
    pattern = r"(?:https?://)?boards\.420chan\.org/([^/?#]+)/thread/(\d+)"
    test = ("https://boards.420chan.org/ani/thread/33251/chow-chows", {
        "pattern": r"https://boards\.420chan\.org/ani/src/\d+\.jpg",
        "content": "b07c803b0da78de159709da923e54e883c100934",
        "count": 2,
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://api.420chan.org/{}/res/{}.json".format(
            self.board, self.thread)
        posts = self.request(url).json()["posts"]

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : posts[0].get("sub") or posts[0]["com"][:50],
        }

        yield Message.Directory, data
        for post in posts:
            if "filename" in post:
                post.update(data)
                post["extension"] = post["ext"][1:]
                url = "https://boards.420chan.org/{}/src/{}{}".format(
                    post["board"], post["filename"], post["ext"])
                yield Message.Url, url, post


class _420chanBoardExtractor(Extractor):
    """Extractor for 420chan boards"""
    category = "420chan"
    subcategory = "board"
    pattern = r"(?:https?://)?boards\.420chan\.org/([^/?#]+)/\d*$"
    test = ("https://boards.420chan.org/po/", {
        "pattern": _420chanThreadExtractor.pattern,
        "count": ">= 100",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def items(self):
        url = "https://api.420chan.org/{}/threads.json".format(self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "https://boards.420chan.org/{}/thread/{}/".format(
                    self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = _420chanThreadExtractor
                yield Message.Queue, url, thread
