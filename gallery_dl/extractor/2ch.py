# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://2ch.hk/"""

from .common import Extractor, Message
from .. import text, util


class _2chThreadExtractor(Extractor):
    """Extractor for 2ch threads"""
    category = "2ch"
    subcategory = "thread"
    root = "https://2ch.hk"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{tim}{filename:? //}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?2ch\.hk/([^/?#]+)/res/(\d+)"
    example = "https://2ch.hk/a/res/12345.html"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = f"{self.root}/{self.board}/res/{self.thread}.json"
        posts = self.request_json(url)["threads"][0]["posts"]

        op = posts[0]
        title = op.get("subject") or text.remove_html(op["comment"])

        thread = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
        }

        yield Message.Directory, thread
        for post in posts:
            if files := post.get("files"):
                post["post_name"] = post["name"]
                post["date"] = text.parse_timestamp(post["timestamp"])
                del post["files"]
                del post["name"]

                for file in files:
                    file.update(thread)
                    file.update(post)

                    file["filename"] = file["fullname"].rpartition(".")[0]
                    file["tim"], _, file["extension"] = \
                        file["name"].rpartition(".")

                    yield Message.Url, self.root + file["path"], file


class _2chBoardExtractor(Extractor):
    """Extractor for 2ch boards"""
    category = "2ch"
    subcategory = "board"
    root = "https://2ch.hk"
    pattern = r"(?:https?://)?2ch\.hk/([^/?#]+)/?$"
    example = "https://2ch.hk/a/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match[1]

    def items(self):
        base = f"{self.root}/{self.board}"

        # index page
        url = f"{base}/index.json"
        index = self.request_json(url)
        index["_extractor"] = _2chThreadExtractor
        for thread in index["threads"]:
            url = f"{base}/res/{thread['thread_num']}.html"
            yield Message.Queue, url, index

        # pages 1..n
        for n in util.advance(index["pages"], 1):
            url = f"{base}/{n}.json"
            page = self.request_json(url)
            page["_extractor"] = _2chThreadExtractor
            for thread in page["threads"]:
                url = f"{base}/res/{thread['thread_num']}.html"
                yield Message.Queue, url, page
