# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.2chan.net/"""

from .common import Extractor, Message
from .. import text


class FutabaThreadExtractor(Extractor):
    """Extractor for images from threads on www.2chan.net"""
    category = "2chan"
    subcategory = "thread"
    directory_fmt = ["{category}", "{board_name}", "{thread}"]
    filename_fmt = "{tim}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    urlfmt = "https://{server}.2chan.net/{board}/src/{filename}"
    pattern = [r"(?:https?://)?(([^.]+)\.2chan\.net/([^/]+)/res/(\d+))"]
    test = [("http://dec.2chan.net/70/res/947.htm", {
        "url": "c5c12b80b290e224b6758507b3bb952044f4595b",
        "keyword": "4bd22e7a9c3636faecd6ea7082509e8655e10dd0",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        url, self.server, self.board, self.thread = match.groups()
        self.url = "https://" + url + ".htm"

    def items(self):
        page = self.request(self.url).text
        data = self.get_metadata(page)
        yield Message.Version, 1
        yield Message.Directory, data
        for post in self.posts(page):
            if "filename" not in post:
                continue
            post.update(data)
            url = self.urlfmt.format_map(post)
            yield Message.Url, url, post

    def get_metadata(self, page):
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
        if '<a href="/' in post:
            self._extract_image(post, data)
            data["tim"], _, data["extension"] = data["filename"].partition(".")
            data["time"] = data["tim"][:-3]
            data["ext"] = "." + data["extension"]
        return data

    @staticmethod
    def _extract_post(post):
        return text.extract_all(post, (
            ("no"  , 'name="', '"'),
            ("post", '<b>', '</b>'),
            ("name", '<b>', ' </b>'),
            ("now" , '</font> ', ' '),
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
