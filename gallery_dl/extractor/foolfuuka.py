# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for FoolFuuka 4chan archives"""

from .common import BaseExtractor, Message
from .. import text
import itertools


class FoolfuukaExtractor(BaseExtractor):
    """Base extractor for FoolFuuka based boards/archives"""
    basecategory = "foolfuuka"
    filename_fmt = "{timestamp_ms} {filename_media}.{extension}"
    archive_fmt = "{board[shortname]}_{num}_{timestamp}"
    external = "default"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        if self.category == "b4k":
            self.remote = self._remote_direct
        elif self.category == "archivedmoe":
            self.referer = False

    def items(self):
        yield Message.Directory, self.metadata()
        for post in self.posts():
            media = post["media"]
            if not media:
                continue
            url = media["media_link"]

            if not url and "remote_media_link" in media:
                url = self.remote(media)
            if url and url[0] == "/":
                url = self.root + url

            post["filename"], _, post["extension"] = \
                media["media"].rpartition(".")
            post["filename_media"] = media["media_filename"].rpartition(".")[0]
            post["timestamp_ms"] = text.parse_int(
                media["media_orig"].rpartition(".")[0])
            yield Message.Url, url, post

    def metadata(self):
        """Return general metadata"""

    def posts(self):
        """Return an iterable with all relevant posts"""

    def remote(self, media):
        """Resolve a remote media link"""
        page = self.request(media["remote_media_link"]).text
        url = text.extr(page, 'http-equiv="Refresh" content="0; url=', '"')
        if url.endswith(".webm") and \
                url.startswith("https://thebarchive.com/"):
            return url[:-1]
        return url

    @staticmethod
    def _remote_direct(media):
        return media["remote_media_link"]


BASE_PATTERN = FoolfuukaExtractor.update({
    "4plebs": {
        "root": "https://archive.4plebs.org",
        "pattern": r"(?:archive\.)?4plebs\.org",
    },
    "archivedmoe": {
        "root": "https://archived.moe",
        "pattern": r"archived\.moe",
    },
    "archiveofsins": {
        "root": "https://archiveofsins.com",
        "pattern": r"(?:www\.)?archiveofsins\.com",
    },
    "b4k": {
        "root": "https://arch.b4k.co",
        "pattern": r"arch\.b4k\.co",
    },
    "desuarchive": {
        "root": "https://desuarchive.org",
        "pattern": r"desuarchive\.org",
    },
    "fireden": {
        "root": "https://boards.fireden.net",
        "pattern": r"boards\.fireden\.net",
    },
    "palanq": {
        "root": "https://archive.palanq.win",
        "pattern": r"archive\.palanq\.win",
    },
    "rbt": {
        "root": "https://rbt.asia",
        "pattern": r"(?:rbt\.asia|(?:archive\.)?rebeccablacktech\.com)",
    },
    "thebarchive": {
        "root": "https://thebarchive.com",
        "pattern": r"thebarchive\.com",
    },
})


class FoolfuukaThreadExtractor(FoolfuukaExtractor):
    """Base extractor for threads on FoolFuuka based boards/archives"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board[shortname]}",
                     "{thread_num} {title|comment[:50]}")
    pattern = BASE_PATTERN + r"/([^/?#]+)/thread/(\d+)"
    example = "https://archived.moe/a/thread/12345/"

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board = self.groups[-2]
        self.thread = self.groups[-1]
        self.data = None

    def metadata(self):
        url = self.root + "/_/api/chan/thread/"
        params = {"board": self.board, "num": self.thread}
        self.data = self.request(url, params=params).json()[self.thread]
        return self.data["op"]

    def posts(self):
        op = (self.data["op"],)
        posts = self.data.get("posts")
        if posts:
            posts = list(posts.values())
            posts.sort(key=lambda p: p["timestamp"])
            return itertools.chain(op, posts)
        return op


class FoolfuukaBoardExtractor(FoolfuukaExtractor):
    """Base extractor for FoolFuuka based boards/archives"""
    subcategory = "board"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:/(?:page/)?(\d*))?$"
    example = "https://archived.moe/a/"

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board = self.groups[-2]
        self.page = self.groups[-1]

    def items(self):
        index_base = "{}/_/api/chan/index/?board={}&page=".format(
            self.root, self.board)
        thread_base = "{}/{}/thread/".format(self.root, self.board)

        page = self.page
        for pnum in itertools.count(text.parse_int(page, 1)):
            with self.request(index_base + format(pnum)) as response:
                try:
                    threads = response.json()
                except ValueError:
                    threads = None

            if not threads:
                return

            for num, thread in threads.items():
                thread["url"] = thread_base + format(num)
                thread["_extractor"] = FoolfuukaThreadExtractor
                yield Message.Queue, thread["url"], thread

            if page:
                return


class FoolfuukaSearchExtractor(FoolfuukaExtractor):
    """Base extractor for search results on FoolFuuka based boards/archives"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search}")
    pattern = BASE_PATTERN + r"/([^/?#]+)/search((?:/[^/?#]+/[^/?#]+)+)"
    example = "https://archived.moe/_/search/text/QUERY/"
    request_interval = (0.5, 1.5)

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.params = params = {}

        key = None
        for arg in self.groups[-1].split("/"):
            if key:
                params[key] = text.unescape(arg)
                key = None
            else:
                key = arg

        board = self.groups[-2]
        if board != "_":
            params["boards"] = board

    def metadata(self):
        return {"search": self.params.get("text", "")}

    def posts(self):
        url = self.root + "/_/api/chan/search/"
        params = self.params.copy()
        params["page"] = text.parse_int(params.get("page"), 1)
        if "filter" not in params:
            params["filter"] = "text"

        while True:
            try:
                data = self.request(url, params=params).json()
            except ValueError:
                return

            if isinstance(data, dict):
                if data.get("error"):
                    return
                posts = data["0"]["posts"]
            elif isinstance(data, list):
                posts = data[0]["posts"]
            else:
                return

            yield from posts
            if len(posts) <= 3:
                return
            params["page"] += 1


class FoolfuukaGalleryExtractor(FoolfuukaExtractor):
    """Base extractor for FoolFuuka galleries"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{board}", "gallery")
    pattern = BASE_PATTERN + r"/([^/?#]+)/gallery(?:/(\d+))?"
    example = "https://archived.moe/a/gallery"

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)

        board = match.group(match.lastindex)
        if board.isdecimal():
            self.board = match.group(match.lastindex-1)
            self.pages = (board,)
        else:
            self.board = board
            self.pages = map(format, itertools.count(1))

    def metadata(self):
        return {"board": self.board}

    def posts(self):
        base = "{}/_/api/chan/gallery/?board={}&page=".format(
            self.root, self.board)

        for page in self.pages:
            with self.request(base + page) as response:
                posts = response.json()
            if not posts:
                return
            yield from posts
