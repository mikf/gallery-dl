# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://8chan.moe/"""

from .common import Extractor, Message
from .. import text
from ..cache import memcache
from datetime import datetime, timedelta
import itertools

BASE_PATTERN = r"(?:https?://)?8chan\.(moe|se|cc)"


class _8chanExtractor(Extractor):
    """Base class for 8chan extractors"""
    category = "8chan"
    root = "https://8chan.moe"

    def __init__(self, match):
        self.root = "https://8chan." + match.group(1)
        Extractor.__init__(self, match)

    @memcache()
    def _prepare_cookies(self):
        # fetch captcha cookies
        # (necessary to download without getting interrupted)
        now = datetime.utcnow()
        url = self.root + "/captcha.js"
        params = {"d": now.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (UTC)")}
        self.request(url, params=params).content

        # adjust cookies
        # - remove 'expires' timestamp
        # - move 'captchaexpiration' value forward by 1 month)
        domain = self.root.rpartition("/")[2]
        for cookie in self.session.cookies:
            if cookie.domain.endswith(domain):
                cookie.expires = None
                if cookie.name == "captchaexpiration":
                    cookie.value = (now + timedelta(30, 300)).strftime(
                        "%a, %d %b %Y %H:%M:%S GMT")

        return self.session.cookies


class _8chanThreadExtractor(_8chanExtractor):
    """Extractor for 8chan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{boardUri}",
                     "{threadId} {subject[:50]}")
    filename_fmt = "{postId}{num:?-//} {filename[:200]}.{extension}"
    archive_fmt = "{boardUri}_{postId}_{num}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/res/(\d+)"
    test = (
        ("https://8chan.moe/vhs/res/4.html", {
            "pattern": r"https://8chan\.moe/\.media/[0-9a-f]{64}\.\w+$",
            "count": 14,
            "keyword": {
                "archived": False,
                "autoSage": False,
                "boardDescription": "Film and Cinema",
                "boardMarkdown": None,
                "boardName": "Movies",
                "boardUri": "vhs",
                "creation": r"re:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z",
                "cyclic": False,
                "email": None,
                "id": "re:^[0-9a-f]{6}$",
                "locked": False,
                "markdown": str,
                "maxFileCount": 5,
                "maxFileSize": "32.00 MB",
                "maxMessageLength": 8001,
                "message": str,
                "mime": str,
                "name": "Anonymous",
                "num": int,
                "originalName": str,
                "path": r"re:/.media/[0-9a-f]{64}\.\w+$",
                "pinned": False,
                "postId": int,
                "signedRole": None,
                "size": int,
                "threadId": 4,
                "thumb": r"re:/.media/t_[0-9a-f]{64}$",
                "uniquePosters": 9,
                "usesCustomCss": True,
                "usesCustomJs": False,
                "wsPort": 8880,
                "wssPort": 2087,
            },
        }),
        ("https://8chan.se/vhs/res/4.html"),
        ("https://8chan.cc/vhs/res/4.html"),
    )

    def __init__(self, match):
        _8chanExtractor.__init__(self, match)
        _, self.board, self.thread = match.groups()

    def items(self):
        # fetch thread data
        url = "{}/{}/res/{}.".format(self.root, self.board, self.thread)
        self.session.headers["Referer"] = url + "html"
        thread = self.request(url + "json").json()
        thread["postId"] = thread["threadId"]
        thread["_http_headers"] = {"Referer": url + "html"}

        try:
            self.session.cookies = self._prepare_cookies()
        except Exception as exc:
            self.log.debug("Failed to fetch captcha cookies:  %s: %s",
                           exc.__class__.__name__, exc, exc_info=True)

        # download files
        posts = thread.pop("posts", ())
        yield Message.Directory, thread
        for post in itertools.chain((thread,), posts):
            files = post.pop("files", ())
            if not files:
                continue
            thread.update(post)
            for num, file in enumerate(files):
                file.update(thread)
                file["num"] = num
                text.nameext_from_url(file["originalName"], file)
                yield Message.Url, self.root + file["path"], file


class _8chanBoardExtractor(_8chanExtractor):
    """Extractor for 8chan boards"""
    subcategory = "board"
    pattern = BASE_PATTERN + r"/([^/?#]+)/(?:(\d+)\.html)?$"
    test = (
        ("https://8chan.moe/vhs/"),
        ("https://8chan.moe/vhs/2.html", {
            "pattern": _8chanThreadExtractor.pattern,
            "count": 23,
        }),
        ("https://8chan.se/vhs/"),
        ("https://8chan.cc/vhs/"),
    )

    def __init__(self, match):
        _8chanExtractor.__init__(self, match)
        _, self.board, self.page = match.groups()
        self.session.headers["Referer"] = self.root + "/"

    def items(self):
        page = text.parse_int(self.page, 1)
        url = "{}/{}/{}.json".format(self.root, self.board, page)
        board = self.request(url).json()
        threads = board["threads"]

        while True:
            for thread in threads:
                thread["_extractor"] = _8chanThreadExtractor
                url = "{}/{}/res/{}.html".format(
                    self.root, self.board, thread["threadId"])
                yield Message.Queue, url, thread

            page += 1
            if page > board["pageCount"]:
                return
            url = "{}/{}/{}.json".format(self.root, self.board, page)
            threads = self.request(url).json()["threads"]
