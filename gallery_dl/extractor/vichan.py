# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for vichan imageboards"""

from .common import BaseExtractor, Message
from .. import text


class VichanExtractor(BaseExtractor):
    """Base class for vichan extractors"""
    basecategory = "vichan"


BASE_PATTERN = VichanExtractor.update({
    "8kun": {
        "root": "https://8kun.top",
        "pattern": r"8kun\.top",
    },
    "smugloli": {
        "root": None,
        "pattern": r"smuglo(?:\.li|li\.net)",
    },
    "gurochan": {
        "root": "https://boards.guro.cx",
        "pattern": r"boards\.guro\.cx",
    },
})


class VichanThreadExtractor(VichanExtractor):
    """Extractor for vichan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/res/(\d+)"
    example = "https://8kun.top/a/res/12345.html"

    def items(self):
        board = self.groups[-2]
        thread = self.groups[-1]
        url = f"{self.root}/{board}/res/{thread}.json"
        posts = self.request_json(url)["posts"]

        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])
        process = (self._process_8kun if self.category == "8kun" else
                   self._process)
        data = {
            "board" : board,
            "thread": thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Directory, "", data
        for post in posts:
            if "filename" in post:
                yield process(post, data)
                if "extra_files" in post:
                    for post["num"], filedata in enumerate(
                            post["extra_files"], 1):
                        yield process(post, filedata)

    def _process(self, post, data):
        post.update(data)
        ext = post["ext"]
        post["extension"] = ext[1:]
        post["url"] = url = \
            f"{self.root}/{post['board']}/src/{post['tim']}{ext}"
        return Message.Url, url, post

    def _process_8kun(self, post, data):
        post.update(data)
        ext = post["ext"]
        tim = post["tim"]

        if len(tim) > 16:
            url = f"https://media.128ducks.com/file_store/{tim}{ext}"
        else:
            url = f"https://media.128ducks.com/{post['board']}/src/{tim}{ext}"

        post["url"] = url
        post["extension"] = ext[1:]
        return Message.Url, url, post


class VichanBoardExtractor(VichanExtractor):
    """Extractor for vichan boards"""
    subcategory = "board"
    pattern = rf"{BASE_PATTERN}/([^/?#]+)(?:/index|/catalog|/\d+|/?$)"
    example = "https://8kun.top/a/"

    def items(self):
        board = self.groups[-1]
        url = f"{self.root}/{board}/threads.json"
        threads = self.request_json(url)

        for page in threads:
            for thread in page["threads"]:
                url = f"{self.root}/{board}/res/{thread['no']}.html"
                thread["page"] = page["page"]
                thread["_extractor"] = VichanThreadExtractor
                yield Message.Queue, url, thread
