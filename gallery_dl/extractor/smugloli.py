# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://smuglo.li/"""

from .common import Extractor, Message
from .. import text


class SmugloliThreadExtractor(Extractor):
    """Extractor for smugloli threads"""
    category = "smugloli"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board}", "{thread} {title}")
    filename_fmt = "{time}{num:?-//} {filename}.{extension}"
    archive_fmt = "{board}_{thread}_{tim}"
    pattern = r"(?:https?://)?(smuglo(?:\.li|li\.net))/([^/]+)/res/(\d+)\.html"
    test = (
        ("https://smuglo.li/a/res/1154380.html", {
            "pattern": r"https://smug.+/a/src/\d+(-\d)?\.\w+",
            "count": ">= 18",
            "keyword": {
                "board": "a",
                "thread": "1154380",
                "title": "Mob Psycho 100 Season 3",
            },
        }),
        ("https://smugloli.net/a/res/1145409.html"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.domain, self.board, self.thread = match.groups()

    def items(self):
        url = "https://{}/{}/res/{}.json".format(
            self.domain, self.board, self.thread)
        posts = self.request(url).json()["posts"]
        title = posts[0].get("sub") or text.remove_html(posts[0]["com"])
        process = self._process

        data = {
            "board" : self.board,
            "thread": self.thread,
            "title" : text.unescape(title)[:50],
            "num"   : 0,
        }

        yield Message.Directory, data
        for post in posts:
            if "filename" in post:
                yield process(post, data)
                if "extra_files" in post:
                    for post["num"], filedata in enumerate(
                            post["extra_files"], 1):
                        yield process(post, filedata)

    def _process(self, post, data):
        post.update(data)
        post["extension"] = post["ext"][1:]
        post["url"] = "https://{}/{}/src/{}{}".format(
            self.domain, post["board"], post["tim"], post["ext"])
        return Message.Url, post["url"], post


class SmugloliBoardExtractor(Extractor):
    """Extractor for smugloli boards"""
    category = "smugloli"
    subcategory = "board"
    pattern = (r"(?:https?://)?(smuglo(?:\.li|li\.net))"
               r"/([^/?#]+)(?:/(?:index|catalog|\d{1,2})\.html)?/?$")
    test = (
        ("https://smuglo.li/a/", {
            "pattern": SmugloliThreadExtractor.pattern,
            "count": ">= 100",
        }),
        ("https://smuglo.li/a/1.html"),
        ("https://smuglo.li/cute/catalog.html"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.domain, self.board = match.groups()

    def items(self):
        url = "https://{}/{}/threads.json".format(self.domain, self.board)
        threads = self.request(url).json()

        for page in threads:
            for thread in page["threads"]:
                url = "{}/{}/res/{}.html".format(
                    self.domain, self.board, thread["no"])
                thread["page"] = page["page"]
                thread["_extractor"] = SmugloliThreadExtractor
                yield Message.Queue, url, thread
