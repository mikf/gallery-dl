# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://4archive.org/"""

from .common import Extractor, Message
from .. import text, util


class _4archiveThreadExtractor(Extractor):
    """Extractor for 4archive threads"""
    category = "4archive"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{no} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{no}"
    root = "https://4archive.org"
    referer = False
    pattern = r"(?:https?://)?4archive\.org/board/([^/?#]+)/thread/(\d+)"
    example = "https://4archive.org/board/a/thread/12345/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()

    def items(self):
        url = "{}/board/{}/thread/{}".format(
            self.root, self.board, self.thread)
        page = self.request(url).text
        data = self.metadata(page)
        posts = self.posts(page)

        if not data["title"]:
            data["title"] = posts[0]["com"][:50]

        for post in posts:
            post.update(data)
            post["time"] = int(util.datetime_to_timestamp(post["date"]))
            yield Message.Directory, post
            if "url" in post:
                yield Message.Url, post["url"], text.nameext_from_url(
                    post["filename"], post)

    def metadata(self, page):
        return {
            "board" : self.board,
            "thread": text.parse_int(self.thread),
            "title" : text.unescape(text.extr(
                page, 'class="subject">', "</span>"))
        }

    def posts(self, page):
        return [
            self.parse(post)
            for post in page.split('class="postContainer')[1:]
        ]

    @staticmethod
    def parse(post):
        extr = text.extract_from(post)
        data = {
            "name": extr('class="name">', "</span>"),
            "date": text.parse_datetime(
                extr('class="dateTime postNum" >', "<").strip(),
                "%Y-%m-%d %H:%M:%S"),
            "no"  : text.parse_int(extr('href="#p', '"')),
        }
        if 'class="file"' in post:
            extr('class="fileText"', ">File: <a")
            data.update({
                "url"     : extr('href="', '"'),
                "filename": extr(
                    'rel="noreferrer noopener"', "</a>").strip()[1:],
                "size"    : text.parse_bytes(extr(" (", ", ")[:-1]),
                "width"   : text.parse_int(extr("", "x")),
                "height"  : text.parse_int(extr("", "px")),
            })
        extr("<blockquote ", "")
        data["com"] = text.unescape(text.remove_html(
            extr(">", "</blockquote>")))
        return data


class _4archiveBoardExtractor(Extractor):
    """Extractor for 4archive boards"""
    category = "4archive"
    subcategory = "board"
    root = "https://4archive.org"
    pattern = r"(?:https?://)?4archive\.org/board/([^/?#]+)(?:/(\d+))?/?$"
    example = "https://4archive.org/board/a/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board = match.group(1)
        self.num = text.parse_int(match.group(2), 1)

    def items(self):
        data = {"_extractor": _4archiveThreadExtractor}
        while True:
            url = "{}/board/{}/{}".format(self.root, self.board, self.num)
            page = self.request(url).text
            if 'class="thread"' not in page:
                return
            for thread in text.extract_iter(page, 'class="thread" id="t', '"'):
                url = "{}/board/{}/thread/{}".format(
                    self.root, self.board, thread)
                yield Message.Queue, url, data
            self.num += 1
