# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
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
        self.session.headers["Referer"] = self.root
        if self.category == "b4k":
            self.remote = self._remote_direct

    def items(self):
        yield Message.Directory, self.metadata()
        for post in self.posts():
            media = post["media"]
            if not media:
                continue
            url = media["media_link"]

            if not url and "remote_media_link" in media:
                url = self.remote(media)
            if url.startswith("/"):
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
        needle = '<meta http-equiv="Refresh" content="0; url='
        page = self.request(media["remote_media_link"]).text
        return text.extract(page, needle, '"')[0]

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
    "rozenarcana": {
        "root": "https://archive.alice.al",
        "pattern": r"(?:archive\.)?alice\.al",
    },
    "tokyochronos": {
        "root": "https://www.tokyochronos.net",
        "pattern": r"(?:www\.)?tokyochronos\.net",
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
    test = (
        ("https://archive.4plebs.org/tg/thread/54059290", {
            "url": "fd823f17b5001442b941fddcd9ec91bafedfbc79",
        }),
        ("https://archived.moe/gd/thread/309639/", {
            "url": "fdd533840e2d535abd162c02d6dfadbc12e2dcd8",
            "content": "c27e2a7be3bc989b5dd859f7789cc854db3f5573",
        }),
        ("https://archived.moe/a/thread/159767162/", {
            "url": "ffec05a1a1b906b5ca85992513671c9155ee9e87",
        }),
        ("https://archiveofsins.com/h/thread/4668813/", {
            "url": "f612d287087e10a228ef69517cf811539db9a102",
            "content": "0dd92d0d8a7bf6e2f7d1f5ac8954c1bcf18c22a4",
        }),
        ("https://arch.b4k.co/meta/thread/196/", {
            "url": "d309713d2f838797096b3e9cb44fe514a9c9d07a",
        }),
        ("https://desuarchive.org/a/thread/159542679/", {
            "url": "e7d624aded15a069194e38dc731ec23217a422fb",
        }),
        ("https://boards.fireden.net/sci/thread/11264294/", {
            "url": "61cab625c95584a12a30049d054931d64f8d20aa",
        }),
        ("https://archive.alice.al/c/thread/2849220/", {
            "url": "632e2c8de05de6b3847685f4bf1b4e5c6c9e0ed5",
        }),
        ("https://www.tokyochronos.net/a/thread/241664141/", {
            "url": "ae03852cf44e3dcfce5be70274cb1828e1dbb7d6",
        }),
        ("https://rbt.asia/g/thread/61487650/", {
            "url": "fadd274b25150a1bdf03a40c58db320fa3b617c4",
        }),
        ("https://archive.rebeccablacktech.com/g/thread/61487650/", {
            "url": "fadd274b25150a1bdf03a40c58db320fa3b617c4",
        }),
        ("https://thebarchive.com/b/thread/739772332/", {
            "url": "e8b18001307d130d67db31740ce57c8561b5d80c",
        }),
    )

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board = match.group(match.lastindex-1)
        self.thread = match.group(match.lastindex)
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
    pattern = BASE_PATTERN + r"/([^/?#]+)/\d*$"
    test = (
        ("https://archive.4plebs.org/tg/"),
        ("https://archived.moe/gd/"),
        ("https://archiveofsins.com/h/"),
        ("https://arch.b4k.co/meta/"),
        ("https://desuarchive.org/a/"),
        ("https://boards.fireden.net/sci/"),
        ("https://archive.alice.al/c/"),
        ("https://www.tokyochronos.net/a/"),
        ("https://rbt.asia/g/"),
        ("https://thebarchive.com/b/"),
    )

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board = match.group(match.lastindex)

    def items(self):
        index_base = "{}/_/api/chan/index/?board={}&page=".format(
            self.root, self.board)
        thread_base = "{}/{}/thread/".format(self.root, self.board)

        for page in itertools.count(1):
            with self.request(index_base + format(page)) as response:
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


class FoolfuukaSearchExtractor(FoolfuukaExtractor):
    """Base extractor for search results on FoolFuuka based boards/archives"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search}")
    pattern = BASE_PATTERN + r"/([^/?#]+)/search((?:/[^/?#]+/[^/?#]+)+)"
    request_interval = 1.0
    test = (
        ("https://archive.4plebs.org/_/search/text/test/"),
        ("https://archived.moe/_/search/text/test/"),
        ("https://archiveofsins.com/_/search/text/test/"),
        ("https://archiveofsins.com/_/search/text/test/"),
        ("https://desuarchive.org/_/search/text/test/"),
        ("https://boards.fireden.net/_/search/text/test/"),
        ("https://archive.alice.al/_/search/text/test/"),
        ("https://www.tokyochronos.net/_/search/text/test/"),
        ("https://rbt.asia/_/search/text/test/"),
        ("https://thebarchive.com/_/search/text/test/"),
    )

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.params = params = {}
        args = match.group(match.lastindex).split("/")
        key = None

        for arg in args:
            if key:
                params[key] = text.unescape(arg)
                key = None
            else:
                key = arg

        board = match.group(match.lastindex-1)
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
    test = (
        ("https://archive.4plebs.org/tg/gallery/1"),
        ("https://archived.moe/gd/gallery/2"),
        ("https://archiveofsins.com/h/gallery/3"),
        ("https://arch.b4k.co/meta/gallery/"),
        ("https://desuarchive.org/a/gallery/5"),
        ("https://boards.fireden.net/sci/gallery/6"),
        ("https://archive.alice.al/c/gallery/7"),
        ("https://www.tokyochronos.net/a/gallery/7"),
        ("https://rbt.asia/g/gallery/8"),
        ("https://thebarchive.com/b/gallery/9"),
    )

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
