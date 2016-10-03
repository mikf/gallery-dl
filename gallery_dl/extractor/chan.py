# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for different Futaba Channel boards"""

from .common import Extractor, Message
from .. import text

class ChanThreadExtractor(Extractor):
    """Base class for extractors for Futaba Channel boards"""
    category = "chan"
    subcategory = "thread"
    directory_fmt = ["{category}", "{board}-{thread}"]
    filename_fmt = "{tim}-{filename}{ext}"
    api_url = ""
    file_url = ""

    def __init__(self, match):
        Extractor.__init__(self)
        self.metadata = {
            "board": match.group(1),
            "thread": match.group(2),
        }

    def items(self):
        yield Message.Version, 1
        url = self.api_url.format_map(self.metadata)
        posts = self.request(url).json()["posts"]
        self.metadata["title"] = self.get_thread_title(posts[0])
        yield Message.Directory, self.metadata
        for post in posts:
            if "filename" not in post:
                continue
            post.update(self.metadata)
            yield Message.Url, self.file_url.format_map(post), post
            if "extra_files" in post:
                for file in post["extra_files"]:
                    post.update(file)
                    yield Message.Url, self.file_url.format_map(post), post

    @staticmethod
    def get_thread_title(post):
        """Return thread title from first post"""
        title = post["sub"] if "sub" in post else text.remove_html(post["com"])
        return text.unescape(title)[:50]
