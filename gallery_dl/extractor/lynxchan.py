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
        "root": "https://bbw-chan.link",
        "pattern": r"bbw-chan\.(?:link|nl)",
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
    example = "https://endchan.org/a/res/12345.html"

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
    example = "https://endchan.org/a/"

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
