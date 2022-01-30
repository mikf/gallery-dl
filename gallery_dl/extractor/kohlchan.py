# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kohlchan.net/"""

from .common import Extractor, Message
from .. import text


class _KohlchanThreadExtractor(Extractor):
    """Extractor for Kohlchan threads"""
    category = "kohlchan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{tim}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?kohlchan\.net/([^/]+)/res/(\d+)"
    test = ()

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://kohlchan.net/{}/res/{}.json".format(self.board, self.thread)
        thread = self.request(url).json()
        title = thread.get("subject") or text.remove_html(thread.get("message"))
        replies = thread["posts"]
        process = self._process

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Version, 1
        yield Message.Directory, data
        
        if "files" in thread:
            for thread["num"], filedata in enumerate(
                    thread["files"]):
                yield process(thread, filedata)
        	
        for post in replies:
            if "files" in post:
                for post["num"], filedata in enumerate(
                        post["files"]):
                    yield process(post, filedata)

    @staticmethod
    def _process(post, data):
        post.update(data)
        url = ("https://kohlchan.net" +
               post["path"])
        text.nameext_from_url(post["originalName"], post)
        post["tim"] = str(post["postId"]) if ("postId" in post) else str(post["threadId"])
        return Message.Url, url, post


class _KohlchanBoardExtractor(Extractor):
    """Extractor for Kohlchan boards"""
    category = "kohlchan"
    subcategory = "board"
    pattern = r"(?:https?://)?kohlchan\.net/([^/?#]+)/(?:catalog\.html|\d+)"
    test = (
        ("https://kohlchan.net/m/", {
            "pattern": _KohlchanThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://kohlchan.net/a/catalog.html"),
        ("https://kohlchan.net/a/res/4594.html")
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)

    def items(self):
        url = "https://kohlchan.net/{}/catalog.json".format(self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "https://kohlchan.net/{}/res/{}.html".format(
                    self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = _KohlchanThreadExtractor
                yield Message.Queue, url, thread
