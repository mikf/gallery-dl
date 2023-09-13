# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for jschan Imageboards"""

from .common import BaseExtractor, Message
from .. import text
import itertools


class JschanExtractor(BaseExtractor):
    basecategory = "jschan"


BASE_PATTERN = JschanExtractor.update({
    "94chan": {
        "root": "https://94chan.org",
        "pattern": r"94chan\.org"
    }
})


class JschanThreadExtractor(JschanExtractor):
    """Extractor for jschan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}",
                     "{threadId} {subject|nomarkup[:50]}")
    filename_fmt = "{postId}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{postId}_{num}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/thread/(\d+)\.html"
    example = "https://94chan.org/a/thread/12345.html"

    def __init__(self, match):
        JschanExtractor.__init__(self, match)
        index = match.lastindex
        self.board = match.group(index-1)
        self.thread = match.group(index)

    def items(self):
        url = "{}/{}/thread/{}.json".format(
            self.root, self.board, self.thread)
        thread = self.request(url).json()
        thread["threadId"] = thread["postId"]
        posts = thread.pop("replies", ())

        yield Message.Directory, thread
        for post in itertools.chain((thread,), posts):
            files = post.pop("files", ())
            if files:
                thread.update(post)
                thread["count"] = len(files)
                for num, file in enumerate(files):
                    url = self.root + "/file/" + file["filename"]
                    file.update(thread)
                    file["num"] = num
                    file["siteFilename"] = file["filename"]
                    text.nameext_from_url(file["originalFilename"], file)
                    yield Message.Url, url, file


class JschanBoardExtractor(JschanExtractor):
    """Extractor for jschan boards"""
    subcategory = "board"
    pattern = (BASE_PATTERN + r"/([^/?#]+)"
               r"(?:/index\.html|/catalog\.html|/\d+\.html|/?$)")
    example = "https://94chan.org/a/"

    def __init__(self, match):
        JschanExtractor.__init__(self, match)
        self.board = match.group(match.lastindex)

    def items(self):
        url = "{}/{}/catalog.json".format(self.root, self.board)
        for thread in self.request(url).json():
            url = "{}/{}/thread/{}.html".format(
                self.root, self.board, thread["postId"])
            thread["_extractor"] = JschanThreadExtractor
            yield Message.Queue, url, thread
