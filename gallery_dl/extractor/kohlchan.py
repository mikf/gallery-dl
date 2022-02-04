# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kohlchan.net/"""

from .common import Extractor, Message
from .. import text
import itertools


class KohlchanThreadExtractor(Extractor):
    """Extractor for Kohlchan threads"""
    category = "kohlchan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{boardUri}",
                     "{threadId} {subject|message[:50]}")
    filename_fmt = "{postId}{num:?-//} {filename}.{extension}"
    archive_fmt = "{boardUri}_{postId}_{num}"
    pattern = r"(?:https?://)?kohlchan\.net/([^/?#]+)/res/(\d+)"
    test = ("https://kohlchan.net/a/res/4594.html", {
        "pattern": r"https://kohlchan\.net/\.media/[0-9a-f]{64}(\.\w+)?$",
        "count": ">= 80",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://kohlchan.net/{}/res/{}.json".format(
            self.board, self.thread)
        thread = self.request(url).json()
        thread["postId"] = thread["threadId"]
        posts = thread.pop("posts")

        yield Message.Directory, thread

        for post in itertools.chain((thread,), posts):
            files = post.pop("files", ())
            if files:
                thread.update(post)
                for num, file in enumerate(files):
                    file.update(thread)
                    file["num"] = num
                    url = "https://kohlchan.net" + file["path"]
                    text.nameext_from_url(file["originalName"], file)
                    yield Message.Url, url, file


class KohlchanBoardExtractor(Extractor):
    """Extractor for Kohlchan boards"""
    category = "kohlchan"
    subcategory = "board"
    pattern = (r"(?:https?://)?kohlchan\.net"
               r"/([^/?#]+)/(?:(?:catalog|\d+)\.html)?$")
    test = (
        ("https://kohlchan.net/a/", {
            "pattern": KohlchanThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://kohlchan.net/a/2.html"),
        ("https://kohlchan.net/a/catalog.html"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def items(self):
        url = "https://kohlchan.net/{}/catalog.json".format(self.board)
        for thread in self.request(url).json():
            url = "https://kohlchan.net/{}/res/{}.html".format(
                self.board, thread["threadId"])
            thread["_extractor"] = KohlchanThreadExtractor
            yield Message.Queue, url, thread
