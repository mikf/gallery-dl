# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://warosu.org/"""

from .common import Extractor, Message
from .. import text


class WarosuThreadExtractor(Extractor):
    """Extractor for images from threads on warosu.org"""
    category = "warosu"
    subcategory = "thread"
    directory_fmt = ["{category}", "{board}", "{thread} - {title}"]
    filename_fmt = "{tim}-{filename}{ext}"
    pattern = [r"(?:https?://)?(?:www\.)?warosu\.org/([^/]+)/thread/(\d+)"]
    test = [
        ("https://warosu.org/jp/thread/16656025", {
            "url": "889d57246ed67e491e5b8f7f124e50ea7991e770",
            "keyword": "65607b4630d87767465a5985c81cfa594913c073",
        }),
        ("https://warosu.org/jp/thread/16658073", {
            "url": "4500cf3184b067424fd9883249bd543c905fbecd",
            "keyword": "d88ea2280201a7b04256c852733faff7272d7d11",
            "content": "d48df0a701e6599312bfff8674f4aa5d4fb8db1c",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.board, self.thread = match.groups()

    def items(self):
        url = "https://warosu.org/" + self.board + "/thread/" + self.thread
        page = self.request(url).text
        data = self.get_metadata(page)
        posts = self.posts(page)

        if not data["title"]:
            title = text.remove_html(posts[0]["com"])
            data["title"] = text.unescape(title)[:50]

        yield Message.Version, 1
        yield Message.Directory, data
        for post in self.posts(page):
            if "image" not in post:
                continue
            post.update(data)
            yield Message.Url, post["image"], post

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        boardname = text.extract(page, "<title>", "</title>")[0]
        title = text.extract(page, 'filetitle" itemprop="name">', '<')[0]
        return {
            "board": self.board,
            "board_name": boardname.rpartition(" - ")[2],
            "thread": self.thread,
            "title": title,
        }

    def posts(self, page):
        """Build a list of all post-objects"""
        page = text.extract(page, '<div class="content">', '<table>')[0]
        needle = '<table itemscope itemtype="http://schema.org/Comment">'
        return [self.parse(post) for post in page.split(needle)]

    def parse(self, post):
        """Build post-object by extracting data from an HTML post"""
        data = self._extract_post(post)
        if "<span>File:" in post:
            self._extract_image(post, data)
            part = data["image"].rpartition("/")[2]
            data["tim"], _, data["extension"] = part.partition(".")
            data["ext"] = "." + data["extension"]
        return data

    @staticmethod
    def _extract_post(post):
        data = text.extract_all(post, (
            ("no"  , 'id="p', '"'),
            ("name", '<span itemprop="name">', '</span>'),
            ("time", '<span class="posttime" title="', '000">'),
            ("now" , '', '<'),
            ("com" , '<blockquote><p itemprop="text">', '</p></blockquote>'),
        ))[0]
        data["com"] = text.unescape(text.remove_html(data["com"].strip()))
        return data

    @staticmethod
    def _extract_image(post, data):
        text.extract_all(post, (
            ("fsize"   , '<span>File: ', ', '),
            ("w"       , '', 'x'),
            ("h"       , '', ', '),
            ("filename", '', '<'),
            ("image"   , '<br />\n<a href="', '"'),
        ), 0, data)
        data["filename"] = data["filename"].rpartition(".")[0]
        data["image"] = "https:" + data["image"]
