# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Base classes for extractors for different Futaba Channel-like boards"""

from .common import Extractor, SharedConfigExtractor, Message
from .. import text
import itertools
import operator


class ChanThreadExtractor(Extractor):
    """Base class for extractors for Futaba Channel-like boards"""
    category = "chan"
    subcategory = "thread"
    directory_fmt = ["{category}", "{board}", "{thread} - {title}"]
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
            self.update(post)
            yield Message.Url, self.build_url(post), post
            if "extra_files" in post:
                for file in post["extra_files"]:
                    self.update(post, file)
                    yield Message.Url, self.build_url(post), post

    def update(self, post, data=None):
        """Update keyword dictionary"""
        post.update(data or self.metadata)
        post["extension"] = post["ext"][1:]

    def build_url(self, post):
        """Construct an image url out of a post object"""
        return self.file_url.format_map(post)

    @staticmethod
    def get_thread_title(post):
        """Return thread title from first post"""
        title = post["sub"] if "sub" in post else text.remove_html(post["com"])
        return text.unescape(title)[:50]


class FoolfuukaThreadExtractor(SharedConfigExtractor):
    """Base extractor for FoolFuuka based boards/archives"""
    basecategory = "foolfuuka"
    subcategory = "thread"
    directory_fmt = ["{category}", "{board[shortname]}",
                     "{thread_num}{title:? - //}"]
    filename_fmt = "{media[media]}"
    root = ""
    referer = True

    def __init__(self, match):
        SharedConfigExtractor.__init__(self)
        self.board, self.thread = match.groups()
        self.session.headers["User-Agent"] = "Mozilla 5.0"
        if self.referer:
            self.session.headers["Referer"] = self.root

    def items(self):
        op = True
        yield Message.Version, 1
        for post in self.posts():
            if op:
                yield Message.Directory, post
                op = False
            if not post["media"]:
                continue

            media = post["media"]
            url = media["media_link"]

            if not url and "remote_media_link" in media:
                url = self.remote(media)
            if url.startswith("/"):
                url = self.root + url

            post["extension"] = url.rpartition(".")[2]
            yield Message.Url, url, post

    def posts(self):
        url = self.root + "/_/api/chan/thread/"
        params = {"board": self.board, "num": self.thread}
        data = self.request(url, params=params).json()[self.thread]

        # sort post-objects by their key
        posts = sorted(data.get("posts", {}).items())
        posts = map(operator.itemgetter(1), posts)

        return itertools.chain((data["op"],), posts)

    def remote(self, media):
        needle = '<meta http-equiv="Refresh" content="0; url='
        page = self.request(media["remote_media_link"]).text
        return text.extract(page, needle, '"')[0]
