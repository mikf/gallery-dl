# -*- coding: utf-8 -*-

# Copyright 2017-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.2chan.net/"""

from .common import Extractor, Message
from .. import text


class _2chanThreadExtractor(Extractor):
    """Extractor for images from threads on www.2chan.net"""
    category = "2chan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board_name}", "{thread}")
    filename_fmt = "{tim}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    url_fmt = "https://{server}.2chan.net/{board}/src/{filename}"
    pattern = r"(?:https?://)?([^.]+)\.2chan\.net/([^/]+)/res/(\d+)"
    test = ("http://dec.2chan.net/70/res/4752.htm", {
        "url": "f49aa31340e9a3429226af24e19e01f5b819ca1f",
        "keyword": "44599c21b248e79692b2eb2da12699bd0ed5640a",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.server, self.board, self.thread = match.groups()

    def items(self):
        url = "https://{}.2chan.net/{}/res/{}.htm".format(
            self.server, self.board, self.thread)
        page = self.request(url).text
        data = self.metadata(page)
        yield Message.Directory, data
        for post in self.posts(page):
            if "filename" not in post:
                continue
            post.update(data)
            url = self.url_fmt.format_map(post)
            yield Message.Url, url, post

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        title = text.extract(page, "<title>", "</title>")[0]
        title, _, boardname = title.rpartition(" - ")
        return {
            "server": self.server,
            "title": title,
            "board": self.board,
            "board_name": boardname[:-4],
            "thread": self.thread,
        }

    def posts(self, page):
        """Build a list of all post-objects"""
        page = text.extract(
            page, '<div class="thre"', '<div style="clear:left"></div>')[0]
        return [
            self.parse(post)
            for post in page.split('<table border=0>')
        ]

    def parse(self, post):
        """Build post-object by extracting data from an HTML post"""
        data = self._extract_post(post)
        if data["name"]:
            data["name"] = data["name"].strip()
        path = text.extract(post, '<a href="/', '"')[0]
        if path and not path.startswith("bin/jump"):
            self._extract_image(post, data)
            data["tim"], _, data["extension"] = data["filename"].partition(".")
            data["time"] = data["tim"][:-3]
            data["ext"] = "." + data["extension"]
        return data

    @staticmethod
    def _extract_post(post):
        return text.extract_all(post, (
            ("post", 'class="csb">'   , '<'),
            ("name", 'class="cnm">'   , '<'),
            ("now" , 'class="cnw">'   , '<'),
            ("no"  , 'class="cno">No.', '<'),
            (None  , '<blockquote', ''),
            ("com" , '>', '</blockquote>'),
        ))[0]

    @staticmethod
    def _extract_image(post, data):
        text.extract_all(post, (
            (None      , '_blank', ''),
            ("filename", '>', '<'),
            ("fsize"   , '(', ' '),
        ), 0, data)
