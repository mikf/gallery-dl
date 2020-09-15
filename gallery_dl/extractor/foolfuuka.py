# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for 4chan archives based on FoolFuuka"""

from .common import Extractor, Message, SharedConfigMixin, generate_extractors
from .. import text
import itertools
import operator


class FoolfuukaThreadExtractor(SharedConfigMixin, Extractor):
    """Base extractor for FoolFuuka based boards/archives"""
    basecategory = "foolfuuka"
    subcategory = "thread"
    directory_fmt = ("{category}", "{board[shortname]}",
                     "{thread_num}{title:? - //}")
    archive_fmt = "{board[shortname]}_{num}_{timestamp}"
    pattern_fmt = r"/([^/]+)/thread/(\d+)"
    external = "default"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.board, self.thread = match.groups()
        self.session.headers["Referer"] = self.root
        if self.external == "direct":
            self.remote = self._remote_direct

    def items(self):
        op = True
        yield Message.Version, 1
        for post in self.posts():
            if op:
                yield Message.Directory, post
                op = False
            if not post["media"]:
                continue

            media = post["media"]
            url = media["media_link"]

            if not url and "remote_media_link" in media:
                url = self.remote(media)
            if url.startswith("/"):
                url = self.root + url

            post["filename"], _, post["extension"] = \
                media["media"].rpartition(".")
            yield Message.Url, url, post

    def posts(self):
        """Return an iterable with all posts in this thread"""
        url = self.root + "/_/api/chan/thread/"
        params = {"board": self.board, "num": self.thread}
        data = self.request(url, params=params).json()[self.thread]

        # sort post-objects by key
        posts = sorted(data.get("posts", {}).items())
        posts = map(operator.itemgetter(1), posts)

        return itertools.chain((data["op"],), posts)

    def remote(self, media):
        """Resolve a remote media link"""
        needle = '<meta http-equiv="Refresh" content="0; url='
        page = self.request(media["remote_media_link"]).text
        return text.extract(page, needle, '"')[0]

    @staticmethod
    def _remote_direct(media):
        return media["remote_media_link"]


EXTRACTORS = {
    "4plebs": {
        "name": "_4plebs",
        "root": "https://archive.4plebs.org",
        "pattern": r"(?:archive\.)?4plebs\.org",
        "test-thread": ("https://archive.4plebs.org/tg/thread/54059290", {
            "url": "07452944164b602502b02b24521f8cee5c484d2a",
        }),
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
    },
    "archiveofsins": {
        "root": "https://archiveofsins.com",
        "pattern": r"(?:www\.)?archiveofsins\.com",
        "test-thread": ("https://archiveofsins.com/h/thread/4668813/", {
            "url": "f612d287087e10a228ef69517cf811539db9a102",
            "content": "0dd92d0d8a7bf6e2f7d1f5ac8954c1bcf18c22a4",
        }),
    },
    "b4k": {
        "root": "https://arch.b4k.co",
        "extra": {"external": "direct"},
        "test-thread": ("https://arch.b4k.co/meta/thread/196/", {
            "url": "d309713d2f838797096b3e9cb44fe514a9c9d07a",
        }),
    },
    "desuarchive": {
        "root": "https://desuarchive.org",
        "test-thread": ("https://desuarchive.org/a/thread/159542679/", {
            "url": "3ae1473f6916ac831efe5cc4d4e7d3298ce79406",
        }),
    },
    "fireden": {
        "root": "https://boards.fireden.net",
        "test-thread": ("https://boards.fireden.net/sci/thread/11264294/", {
            "url": "3adfe181ee86a8c23021c705f623b3657a9b0a43",
        }),
    },
    "nyafuu": {
        "root": "https://archive.nyafuu.org",
        "pattern": r"(?:archive\.)?nyafuu\.org",
        "test-thread": ("https://archive.nyafuu.org/c/thread/2849220/", {
            "url": "bbe6f82944a45e359f5c8daf53f565913dc13e4f",
        }),
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
    },
    "thebarchive": {
        "root": "https://thebarchive.com",
        "pattern": r"thebarchive\.com",
        "test-thread": ("https://thebarchive.com/b/thread/739772332/", {
            "url": "e8b18001307d130d67db31740ce57c8561b5d80c",
        }),
    },
}

generate_extractors(EXTRACTORS, globals(), (
    FoolfuukaThreadExtractor,
))
