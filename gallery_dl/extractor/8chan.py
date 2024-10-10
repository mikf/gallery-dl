# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://8chan.moe/"""

from .common import Extractor, Message
from .. import text, util
from ..cache import memcache
from datetime import timedelta
import itertools

BASE_PATTERN = r"(?:https?://)?8chan\.(moe|se|cc)"


class _8chanExtractor(Extractor):
    """Base class for 8chan extractors"""
    category = "8chan"
    root = "https://8chan.moe"

    def __init__(self, match):
        self.root = "https://8chan." + match.group(1)
        Extractor.__init__(self, match)

    def _init(self):
        now = util.datetime_utcnow()
        domain = self.root.rpartition("/")[2]
        self.cookies.set(
            now.strftime("TOS%Y%m%d"), "1", domain=domain)
        self.cookies.set(
            (now - timedelta(1)).strftime("TOS%Y%m%d"), "1", domain=domain)

    @memcache()
    def cookies_prepare(self):
        # fetch captcha cookies
        # (necessary to download without getting interrupted)
        now = util.datetime_utcnow()
        url = self.root + "/captcha.js"
        params = {"d": now.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (UTC)")}
        self.request(url, params=params).content

        # adjust cookies
        # - remove 'expires' timestamp
        # - move 'captchaexpiration' value forward by 1 month
        domain = self.root.rpartition("/")[2]
        for cookie in self.cookies:
            if cookie.domain.endswith(domain):
                cookie.expires = None
                if cookie.name == "captchaexpiration":
                    cookie.value = (now + timedelta(30, 300)).strftime(
                        "%a, %d %b %Y %H:%M:%S GMT")

        return self.cookies


class _8chanThreadExtractor(_8chanExtractor):
    """Extractor for 8chan threads"""
    subcategory = "thread"
    directory_fmt = ("{category}", "{boardUri}",
                     "{threadId} {subject[:50]}")
    filename_fmt = "{postId}{num:?-//} {filename[:200]}.{extension}"
    archive_fmt = "{boardUri}_{postId}_{num}"
    pattern = BASE_PATTERN + r"/([^/?#]+)/res/(\d+)"
    example = "https://8chan.moe/a/res/12345.html"

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
            self.cookies = self.cookies_prepare()
        except Exception as exc:
            self.log.debug("Failed to fetch captcha cookies:  %s: %s",
                           exc.__class__.__name__, exc, exc_info=exc)

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
    example = "https://8chan.moe/a/"

    def __init__(self, match):
        _8chanExtractor.__init__(self, match)
        _, self.board, self.page = match.groups()

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
