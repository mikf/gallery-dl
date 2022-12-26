# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for LynxChan Imageboards"""

from .common import BaseExtractor, Message
from .. import text
import itertools


class LynxchanExtractor(BaseExtractor):
    """Base class for LynxChan extractors"""
    basecategory = "lynxchan"


BASE_PATTERN = LynxchanExtractor.update({
    "bbw-chan": {
        "root": "https://bbw-chan.nl",
        "pattern": r"bbw-chan\.nl",
    },
    "kohlchan": {
        "root": "https://kohlchan.net",
        "pattern": r"kohlchan\.net",
    },
    "endchan": {
        "root": None,
        "pattern": r"endchan\.(?:org|net|gg)",
    },
})


class LynxchanThreadExtractor(LynxchanExtractor):
    """Extractor for LynxChan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{boardUri}",
                     "{threadId} {subject|message[:50]}")
    filename_fmt = "{postId}{num:?-//} {filename}.{extension}"
    archive_fmt = "{boardUri}_{postId}_{num}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/res/(\d+)"
    test = (
        ("https://bbw-chan.nl/bbwdraw/res/499.html", {
            "pattern": r"https://bbw-chan\.nl/\.media/[0-9a-f]{64}(\.\w+)?$",
            "count": ">= 352",
        }),
        ("https://bbw-chan.nl/bbwdraw/res/489.html"),
        ("https://kohlchan.net/a/res/4594.html", {
            "pattern": r"https://kohlchan\.net/\.media/[0-9a-f]{64}(\.\w+)?$",
            "count": ">= 80",
        }),
        ("https://endchan.org/yuri/res/193483.html", {
            "pattern": r"https://endchan\.org/\.media/[^.]+(\.\w+)?$",
            "count"  : ">= 19",
        }),
        ("https://endchan.org/yuri/res/33621.html"),
    )

    def __init__(self, match):
        LynxchanExtractor.__init__(self, match)
        index = match.lastindex
        self.board = match.group(index-1)
        self.thread = match.group(index)

    def items(self):
        url = "{}/{}/res/{}.json".format(self.root, self.board, self.thread)
        thread = self.request(url).json()
        thread["postId"] = thread["threadId"]
        posts = thread.pop("posts", ())

        yield Message.Directory, thread
        for post in itertools.chain((thread,), posts):
            files = post.pop("files", ())
            if files:
                thread.update(post)
                for num, file in enumerate(files):
                    file.update(thread)
                    file["num"] = num
                    url = self.root + file["path"]
                    text.nameext_from_url(file["originalName"], file)
                    yield Message.Url, url, file


class LynxchanBoardExtractor(LynxchanExtractor):
    """Extractor for LynxChan boards"""
    subcategory = "board"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:/index|/catalog|/\d+|/?$)"
    test = (
        ("https://bbw-chan.nl/bbwdraw/", {
            "pattern": LynxchanThreadExtractor.pattern,
            "count": ">= 148",
        }),
        ("https://bbw-chan.nl/bbwdraw/2.html"),
        ("https://kohlchan.net/a/", {
            "pattern": LynxchanThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://kohlchan.net/a/2.html"),
        ("https://kohlchan.net/a/catalog.html"),
        ("https://endchan.org/yuri/", {
            "pattern": LynxchanThreadExtractor.pattern,
            "count"  : ">= 9",
        }),
        ("https://endchan.org/yuri/catalog.html"),
    )

    def __init__(self, match):
        LynxchanExtractor.__init__(self, match)
        self.board = match.group(match.lastindex)

    def items(self):
        url = "{}/{}/catalog.json".format(self.root, self.board)
        for thread in self.request(url).json():
            url = "{}/{}/res/{}.html".format(
                self.root, self.board, thread["threadId"])
            thread["_extractor"] = LynxchanThreadExtractor
            yield Message.Queue, url, thread
