# -*- coding: utf-8 -*-

# Copyright 2017-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.2chan.net/"""

from .common import Extractor, Message
from .. import text


class _2chanThreadExtractor(Extractor):
    """Extractor for 2chan threads"""
    category = "2chan"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board_name}", "{thread}")
    filename_fmt = "{tim}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?([\w-]+)\.2chan\.net/([^/?#]+)/res/(\d+)"
    example = "https://dec.2chan.net/12/res/12345.htm"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.server, self.board, self.thread = match.groups()

    def items(self):
        url = (f"https://{self.server}.2chan.net"
               f"/{self.board}/res/{self.thread}.htm")
        page = self.request(url).text
        data = self.metadata(page)
        yield Message.Directory, "", data
        for post in self.posts(page):
            if "filename" not in post:
                continue
            post.update(data)
            url = (f"https://{post['server']}.2chan.net"
                   f"/{post['board']}/src/{post['filename']}")
            yield Message.Url, url, post

    def metadata(self, page):
        """Collect metadata for extractor-job"""
        title, _, boardname = text.extr(
            page, "<title>", "</title>").rpartition(" - ")
        return {
            "server": self.server,
            "title": title,
            "board": self.board,
            "board_name": boardname[:-4],
            "thread": self.thread,
        }

    def posts(self, page):
        """Build a list of all post-objects"""
        page = text.extr(
            page, '<div class="thre"', '<div style="clear:left"></div>')
        return [
            self.parse(post)
            for post in page.split('<table border=0>')
        ]

    def parse(self, post):
        """Build post-object by extracting data from an HTML post"""
        data = self._extract_post(post)
        if data["name"]:
            data["name"] = data["name"].strip()
        path = text.extr(post, '<a href="/', '"')
        if path and not path.startswith("bin/jump"):
            self._extract_image(post, data)
            data["tim"], _, data["extension"] = data["filename"].partition(".")
            data["time"] = data["tim"][:-3]
            data["ext"] = "." + data["extension"]
        return data

    def _extract_post(self, post):
        return text.extract_all(post, (
            ("post", 'class="csb">'   , '<'),
            ("name", 'class="cnm">'   , '<'),
            ("now" , 'class="cnw">'   , '<'),
            ("no"  , 'class="cno">No.', '<'),
            (None  , '<blockquote', ''),
            ("com" , '>', '</blockquote>'),
        ))[0]

    def _extract_image(self, post, data):
        text.extract_all(post, (
            (None      , '_blank', ''),
            ("filename", '>', '<'),
            ("fsize"   , '(', ' '),
        ), 0, data)
