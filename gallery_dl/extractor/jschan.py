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
    pattern = rf"{BASE_PATTERN}/([^/?#]+)/thread/(\d+)\.html"
    example = "https://94chan.org/a/thread/12345.html"

    def items(self):
        url = f"{self.root}/{self.groups[-2]}/thread/{self.groups[-1]}.json"
        thread = self.request_json(url)
        thread["threadId"] = thread["postId"]
        posts = thread.pop("replies", ())

        yield Message.Directory, "", thread
        for post in itertools.chain((thread,), posts):
            if files := post.pop("files", ()):
                thread.update(post)
                thread["count"] = len(files)
                for num, file in enumerate(files):
                    url = f"{self.root}/file/{file['filename']}"
                    file.update(thread)
                    file["num"] = num
                    file["siteFilename"] = file["filename"]
                    text.nameext_from_url(file["originalFilename"], file)
                    yield Message.Url, url, file


class JschanBoardExtractor(JschanExtractor):
    """Extractor for jschan boards"""
    subcategory = "board"
    pattern = (rf"{BASE_PATTERN}/([^/?#]+)"
               r"(?:/index\.html|/catalog\.html|/\d+\.html|/?$)")
    example = "https://94chan.org/a/"

    def items(self):
        board = self.groups[-1]
        url = f"{self.root}/{board}/catalog.json"
        for thread in self.request_json(url):
            url = f"{self.root}/{board}/thread/{thread['postId']}.html"
            thread["_extractor"] = JschanThreadExtractor
            yield Message.Queue, url, thread
