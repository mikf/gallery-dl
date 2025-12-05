# -*- coding: utf-8 -*-

# Copyright 2015-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.4chan.org/"""

from .common import Extractor, Message
from .. import text


class _4chanThreadExtractor(Extractor):
    """Extractor for 4chan threads"""
    category = "4chan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{tim} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = (r"(?:https?://)?boards\.4chan(?:nel)?\.org"
               r"/([^/]+)/thread/(\d+)")
    example = "https://boards.4channel.org/a/thread/12345/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = f"https://a.4cdn.org/{self.board}/thread/{self.thread}.json"
        posts = self.request_json(url)["posts"]
        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
        }

        yield Message.Directory, "", data
        for post in posts:
            if "filename" in post:
                post.update(data)
                post["extension"] = post["ext"][1:]
                post["filename"] = text.unescape(post["filename"])
                post["_http_signature"] = _detect_null_byte
                url = (f"https://i.4cdn.org"
                       f"/{post['board']}/{post['tim']}{post['ext']}")
                yield Message.Url, url, post


def _detect_null_byte(signature):
    """Return False if all file signature bytes are null"""
    if signature:
        if signature[0]:
            return True
        for byte in signature:
            if byte:
                return True
    return "File data consists of null bytes"


class _4chanBoardExtractor(Extractor):
    """Extractor for 4chan boards"""
    category = "4chan"
    subcategory = "board"
    pattern = r"(?:https?://)?boards\.4chan(?:nel)?\.org/([^/?#]+)/\d*$"
    example = "https://boards.4channel.org/a/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match[1]

    def items(self):
        url = f"https://a.4cdn.org/{self.board}/threads.json"
        threads = self.request_json(url)

        for page in threads:
            for thread in page["threads"]:
                url = (f"https://boards.4chan.org"
                       f"/{self.board}/thread/{thread['no']}/")
                thread["page"] = page["page"]
                thread["_extractor"] = _4chanThreadExtractor
                yield Message.Queue, url, thread
