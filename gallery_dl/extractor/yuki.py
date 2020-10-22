# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://yuki.la/"""

from .common import Extractor, Message
from .. import text


class YukiThreadExtractor(Extractor):
    """Extractor for images from threads on yuki.la"""
    category = "yuki"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread}{title:? - //}")
    filename_fmt = "{time}-{filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?yuki\.la/([^/?#]+)/(\d+)"
    test = (
        ("https://yuki.la/gd/309639", {
            "url": "289e86c5caf673a2515ec5f5f521ac0ae7e189e9",
            "keyword": "01cbe29ae207a5cb7556bcbd5ed481ecdaf32727",
            "content": "c27e2a7be3bc989b5dd859f7789cc854db3f5573",
        }),
        ("https://yuki.la/a/159767162", {
            "url": "cd94d0eb646d279c3b7efb9b7898888e5d44fa93",
            "keyword": "7a4ff90e423c74bd3126fb65d13015decec2fa45",
        }),
        # old thread - missing board name in title and multi-line HTML
        ("https://yuki.la/gif/6877752", {
            "url": "3dbb2f8453490d002416c5fc2fe95b56c129faf9",
            "keyword": "563ef4ae80134d845dddaed7ebe56f5fc41056be",
        }),
        # even older thread - no thread title
        ("https://yuki.la/a/9357051", {
            "url": "010560bf254bd485e48366c3531728bda4b22583",
            "keyword": "7b736c41e307dcfcb84ef495f29299a6ddd06d67",
        }),
    )
    root = "https://yuki.la"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "{}/{}/{}".format(self.root, self.board, self.thread)
        page = self.request(url).text
        data = self.get_metadata(page)

        yield Message.Version, 1
        yield Message.Directory, data
        for post in self.posts(page):
            if "image" in post:
                for key in ("w", "h", "no", "time"):
                    post[key] = text.parse_int(post[key])
                post.update(data)
                yield Message.Url, post["image"], post

    def get_metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0]
        try:
            title, boardname, _ = title.rsplit(" - ", 2)
        except ValueError:
            title = boardname = ""
        else:
            title = title.partition(" - ")[2]
            if not title:
                title, boardname = boardname, ""
        return {
            "board": self.board,
            "board_name": boardname,
            "thread": text.parse_int(self.thread),
            "title": text.unescape(title),
        }

    def posts(self, page):
        """Build a list of all post-objects"""
        return [
            self.parse(post) for post in text.extract_iter(
                page, '<div class="postContainer', '</blockquote>')
        ]

    def parse(self, post):
        """Build post-object by extracting data from an HTML post"""
        data = self._extract_post(post)
        if 'class="file"' in post:
            self._extract_image(post, data)
            part = data["image"].rpartition("/")[2]
            data["tim"], _, data["extension"] = part.partition(".")
            data["ext"] = "." + data["extension"]
        return data

    @staticmethod
    def _extract_post(post):
        data, pos = text.extract_all(post, (
            ("no"  , 'id="pc', '"'),
            ("name", '<span class="name">', '</span>'),
            ("time", 'data-utc="', '"'),
            ("now" , '>', ' <'),
        ))
        data["com"] = text.unescape(text.remove_html(
            post[post.index("<blockquote ", pos):].partition(">")[2]))
        return data

    @staticmethod
    def _extract_image(post, data):
        text.extract_all(post, (
            (None      , '>File:', ''),
            ("fullname", '<a title="', '"'),
            ("image"   , 'href="', '"'),
            ("filename", '>', '<'),
            ("fsize"   , '(', ', '),
            ("w"       , '', 'x'),
            ("h"       , '', ')'),
        ), 0, data)
        filename = data["fullname"] or data["filename"]
        data["filename"] = text.unescape(filename.rpartition(".")[0])
        data["image"] = "https:" + data["image"]
        del data["fullname"]
