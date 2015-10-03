# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for different Futaba Channel boards"""

from .common import SequentialExtractor, Message
from .. import text
import re

class ChanExtractor(SequentialExtractor):

    api_url = ""
    file_url = ""

    def __init__(self, config, category, board, thread):
        SequentialExtractor.__init__(self, config)
        self.metadata = {
            "category": category,
            "board": board,
            "thread": thread,
        }

    def items(self):
        yield Message.Version, 1
        posts = self.request(self.api_url.format(**self.metadata)).json()["posts"]
        self.metadata["title"] = self.get_thread_title(posts[0])
        yield Message.Directory, self.metadata
        for post in posts:
            if "filename" not in post:
                continue
            post.update(self.metadata)
            yield Message.Url, self.file_url.format(**post), post
            if "extra_files" in post:
                for file in post["extra_files"]:
                    post.update(file)
                    yield Message.Url, self.file_url.format(**post), post

    @staticmethod
    def get_thread_title(post):
        """Return thread title from first post"""
        if "sub" in post:
            return post["sub"]
        return text.remove_html(post["com"])[:50]
