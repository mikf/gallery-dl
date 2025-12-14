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
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/res/(\d+)"
    example = "https://endchan.org/a/res/12345.html"

    def items(self):
        url = f"{self.root}/{self.groups[-2]}/res/{self.groups[-1]}.json"
        thread = self.request_json(url)
        thread["postId"] = thread["threadId"]
        posts = thread.pop("posts", ())

        yield Message.Directory, "", thread
        for post in itertools.chain((thread,), posts):
            if files := post.pop("files", ()):
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
    pattern = rf"{BASE_PATTERN}/([^/?#]+)(?:/index|/catalog|/\d+|/?$)"
    example = "https://endchan.org/a/"

    def items(self):
        board = self.groups[-1]
        url = f"{self.root}/{board}/catalog.json"
        for thread in self.request_json(url):
            url = f"{self.root}/{board}/res/{thread['threadId']}.html"
            thread["_extractor"] = LynxchanThreadExtractor
            yield Message.Queue, url, thread
