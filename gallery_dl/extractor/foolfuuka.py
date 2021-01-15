# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for 4chan archives based on FoolFuuka"""

from .common import Extractor, Message, generate_extractors
from .. import text
import itertools


class FoolfuukaExtractor(Extractor):
    """Base extractor for FoolFuuka based boards/archives"""
    basecategory = "foolfuuka"
    archive_fmt = "{board[shortname]}_{num}_{timestamp}"
    external = "default"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.headers["Referer"] = self.root
        if self.external == "direct":
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
        """ """

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


class FoolfuukaThreadExtractor(FoolfuukaExtractor):
    """Base extractor for threads on FoolFuuka based boards/archives"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{board[shortname]}",
                     "{thread_num}{title:? - //}")
    pattern_fmt = r"/([^/?#]+)/thread/(\d+)"

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board, self.thread = match.groups()
        self.data = None

    def metadata(self):
        url = self.root + "/_/api/chan/thread/"
        params = {"board": self.board, "num": self.thread}
        self.data = self.request(url, params=params).json()[self.thread]
        return self.data["op"]

    def posts(self):
        posts = self.data.get("posts")
        if posts:
            posts = list(posts.values())
            posts.sort(key=lambda p: p["timestamp"])
        else:
            posts = ()
        return itertools.chain((self.data["op"],), posts)


class FoolfuukaBoardExtractor(FoolfuukaExtractor):
    """Base extractor for FoolFuuka based boards/archives"""
    subcategory = "board"
    pattern_fmt = r"/([^/?#]+)/\d*$"

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        self.board = match.group(1)

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
                thread["_extractor"] = self.childclass
                yield Message.Queue, thread["url"], thread


class FoolfuukaSearchExtractor(FoolfuukaExtractor):
    """Base extractor for search results on FoolFuuka based boards/archives"""
    subcategory = "search"
    directory_fmt = ("{category}", "search", "{search}")
    pattern_fmt = r"/([^/?#]+)/search((?:/[^/?#]+/[^/?#]+)+)"
    request_interval = 1.0

    def __init__(self, match):
        FoolfuukaExtractor.__init__(self, match)
        board, search = match.groups()

        self.params = params = {}
        args = search.split("/")
        key = None

        for arg in args:
            if key:
                params[key] = text.unescape(arg)
                key = None
            else:
                key = arg
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


EXTRACTORS = {
    "4plebs": {
        "name": "_4plebs",
        "root": "https://archive.4plebs.org",
        "pattern": r"(?:archive\.)?4plebs\.org",
        "test-thread": ("https://archive.4plebs.org/tg/thread/54059290", {
            "url": "07452944164b602502b02b24521f8cee5c484d2a",
        }),
        "test-board": ("https://archive.4plebs.org/tg/",),
        "test-search": ("https://archive.4plebs.org/_/search/text/test/",),
    },
    "archivedmoe": {
        "root": "https://archived.moe",
        "test-thread": (
            ("https://archived.moe/gd/thread/309639/", {
                "url": "fdd533840e2d535abd162c02d6dfadbc12e2dcd8",
                "content": "c27e2a7be3bc989b5dd859f7789cc854db3f5573",
            }),
            ("https://archived.moe/a/thread/159767162/", {
                "url": "ffec05a1a1b906b5ca85992513671c9155ee9e87",
            }),
        ),
        "test-board": ("https://archived.moe/gd/",),
        "test-search": ("https://archived.moe/_/search/text/test/",),
    },
    "archiveofsins": {
        "root": "https://archiveofsins.com",
        "pattern": r"(?:www\.)?archiveofsins\.com",
        "test-thread": ("https://archiveofsins.com/h/thread/4668813/", {
            "url": "f612d287087e10a228ef69517cf811539db9a102",
            "content": "0dd92d0d8a7bf6e2f7d1f5ac8954c1bcf18c22a4",
        }),
        "test-board": ("https://archiveofsins.com/h/",),
        "test-search": ("https://archiveofsins.com/_/search/text/test/",),
    },
    "b4k": {
        "root": "https://arch.b4k.co",
        "extra": {"external": "direct"},
        "test-thread": ("https://arch.b4k.co/meta/thread/196/", {
            "url": "d309713d2f838797096b3e9cb44fe514a9c9d07a",
        }),
        "test-board": ("https://arch.b4k.co/meta/",),
        "test-search": ("https://arch.b4k.co/_/search/text/test/",),
    },
    "desuarchive": {
        "root": "https://desuarchive.org",
        "test-thread": ("https://desuarchive.org/a/thread/159542679/", {
            "url": "3ae1473f6916ac831efe5cc4d4e7d3298ce79406",
        }),
        "test-board": ("https://desuarchive.org/a/",),
        "test-search": ("https://desuarchive.org/_/search/text/test/",),
    },
    "fireden": {
        "root": "https://boards.fireden.net",
        "test-thread": ("https://boards.fireden.net/sci/thread/11264294/", {
            "url": "3adfe181ee86a8c23021c705f623b3657a9b0a43",
        }),
        "test-board": ("https://boards.fireden.net/sci/",),
        "test-search": ("https://boards.fireden.net/_/search/text/test/",),
    },
    "nyafuu": {
        "root": "https://archive.nyafuu.org",
        "pattern": r"(?:archive\.)?nyafuu\.org",
        "test-thread": ("https://archive.nyafuu.org/c/thread/2849220/", {
            "url": "bbe6f82944a45e359f5c8daf53f565913dc13e4f",
        }),
        "test-board": ("https://archive.nyafuu.org/c/",),
        "test-search": ("https://archive.nyafuu.org/_/search/text/test/",),
    },
    "rbt": {
        "root": "https://rbt.asia",
        "pattern": r"(?:rbt\.asia|(?:archive\.)?rebeccablacktech\.com)",
        "test-thread": (
            ("https://rbt.asia/g/thread/61487650/", {
                "url": "61896d9d9a2edb556b619000a308a984307b6d30",
            }),
            ("https://archive.rebeccablacktech.com/g/thread/61487650/", {
                "url": "61896d9d9a2edb556b619000a308a984307b6d30",
            }),
        ),
        "test-board": ("https://rbt.asia/g/",),
        "test-search": ("https://rbt.asia/_/search/text/test/",),
    },
    "thebarchive": {
        "root": "https://thebarchive.com",
        "pattern": r"thebarchive\.com",
        "test-thread": ("https://thebarchive.com/b/thread/739772332/", {
            "url": "e8b18001307d130d67db31740ce57c8561b5d80c",
        }),
        "test-board": ("https://thebarchive.com/b/",),
        "test-search": ("https://thebarchive.com/_/search/text/test/",),
    },
    "_ckey": "childclass",
}

generate_extractors(EXTRACTORS, globals(), (
    FoolfuukaThreadExtractor,
    FoolfuukaBoardExtractor,
    FoolfuukaSearchExtractor,
))
