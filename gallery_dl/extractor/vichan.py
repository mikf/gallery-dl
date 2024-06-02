# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
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
})


class VichanThreadExtractor(VichanExtractor):
    """Extractor for vichan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/res/(\d+)"
    example = "https://8kun.top/a/res/12345.html"

    def __init__(self, match):
        VichanExtractor.__init__(self, match)
        index = match.lastindex
        self.board = match.group(index-1)
        self.thread = match.group(index)

    def items(self):
        url = "{}/{}/res/{}.json".format(self.root, self.board, self.thread)
        posts = self.request(url).json()["posts"]
        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])
        process = (self._process_8kun if self.category == "8kun" else
                   self._process)
        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Directory, data
        for post in posts:
            if "filename" in post:
                yield process(post, data)
                if "extra_files" in post:
                    for post["num"], filedata in enumerate(
                            post["extra_files"], 1):
                        yield process(post, filedata)

    def _process(self, post, data):
        post.update(data)
        post["extension"] = post["ext"][1:]
        post["url"] = "{}/{}/src/{}{}".format(
            self.root, post["board"], post["tim"], post["ext"])
        return Message.Url, post["url"], post

    @staticmethod
    def _process_8kun(post, data):
        post.update(data)
        post["extension"] = post["ext"][1:]

        tim = post["tim"]
        if len(tim) > 16:
            post["url"] = "https://media.128ducks.com/file_store/{}{}".format(
                tim, post["ext"])
        else:
            post["url"] = "https://media.128ducks.com/{}/src/{}{}".format(
                post["board"], tim, post["ext"])

        return Message.Url, post["url"], post


class VichanBoardExtractor(VichanExtractor):
    """Extractor for vichan boards"""
    subcategory = "board"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:/index|/catalog|/\d+|/?$)"
    example = "https://8kun.top/a/"

    def __init__(self, match):
        VichanExtractor.__init__(self, match)
        self.board = match.group(match.lastindex)

    def items(self):
        url = "{}/{}/threads.json".format(self.root, self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "{}/{}/res/{}.html".format(
                    self.root, self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = VichanThreadExtractor
                yield Message.Queue, url, thread
