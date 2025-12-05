# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://2ch.org/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?2ch\.(org|su|life|hk)"


class _2chThreadExtractor(Extractor):
    """Extractor for 2ch threads"""
    category = "2ch"
    subcategory = "thread"
    root = "https://2ch.org"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{tim}{filename:? //}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/res/(\d+)"
    example = "https://2ch.org/a/res/12345.html"

    def __init__(self, match):
        tld = match[1]
        self.root = f"https://2ch.{'org' if tld == 'hk' else tld}"
        Extractor.__init__(self, match)

    def items(self):
        _, board, thread = self.groups
        url = f"{self.root}/{board}/res/{thread}.json"
        posts = self.request_json(url)["threads"][0]["posts"]

        op = posts[0]
        title = op.get("subject") or text.remove_html(op["comment"])

        thread = {
            "board" : board,
            "thread": thread,
            "title" : text.unescape(title)[:50],
        }

        yield Message.Directory, "", thread
        for post in posts:
            if files := post.get("files"):
                post["post_name"] = post["name"]
                post["date"] = self.parse_timestamp(post["timestamp"])
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
    root = "https://2ch.org"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/?$"
    example = "https://2ch.org/a/"

    def __init__(self, match):
        tld = match[1]
        self.root = f"https://2ch.{'su' if tld == 'hk' else tld}"
        Extractor.__init__(self, match)

    def items(self):
        base = f"{self.root}/{self.groups[1]}"

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
