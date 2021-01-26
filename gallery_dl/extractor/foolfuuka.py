# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for 4chan archives based on FoolFuuka"""

from .common import BaseExtractor, Message
from .. import text
import itertools


class FoolfuukaExtractor(BaseExtractor):
    """Base extractor for FoolFuuka based boards/archives"""
    basecategory = "foolfuuka"
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
    },
    "archiveofsins": {
        "root": "https://archiveofsins.com",
        "pattern": r"(?:www\.)?archiveofsins\.com",
    },
    "b4k": {
        "root": "https://arch.b4k.co",
    },
    "desuarchive": {
        "root": "https://desuarchive.org",
    },
    "fireden": {
        "root": "https://boards.fireden.net",
    },
    "nyafuu": {
        "root": "https://archive.nyafuu.org",
        "pattern": r"(?:archive\.)?nyafuu\.org",
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
                     "{thread_num}{title:? - //}")
    pattern = BASE_PATTERN + r"/([^/?#]+)/thread/(\d+)"
    test = (
        ("https://archive.4plebs.org/tg/thread/54059290", {
            "url": "07452944164b602502b02b24521f8cee5c484d2a",
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
            "url": "3ae1473f6916ac831efe5cc4d4e7d3298ce79406",
        }),
        ("https://boards.fireden.net/sci/thread/11264294/", {
            "url": "3adfe181ee86a8c23021c705f623b3657a9b0a43",
        }),
        ("https://archive.nyafuu.org/c/thread/2849220/", {
            "url": "bbe6f82944a45e359f5c8daf53f565913dc13e4f",
        }),
        ("https://rbt.asia/g/thread/61487650/", {
            "url": "61896d9d9a2edb556b619000a308a984307b6d30",
        }),
        ("https://archive.rebeccablacktech.com/g/thread/61487650/", {
            "url": "61896d9d9a2edb556b619000a308a984307b6d30",
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
        ("https://archive.nyafuu.org/c/"),
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
        ("https://archive.nyafuu.org/_/search/text/test/"),
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
