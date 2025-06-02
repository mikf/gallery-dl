# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://poipiku.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?poipiku\.com"


class PoipikuExtractor(Extractor):
    """Base class for poipiku extractors"""
    category = "poipiku"
    root = "https://poipiku.com"
    directory_fmt = ("{category}", "{user_id} {user_name}")
    filename_fmt = "{post_id}_{num}.{extension}"
    archive_fmt = "{post_id}_{num}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.cookies.set(
            "LANG", "en", domain="poipiku.com")
        self.cookies.set(
            "POIPIKU_CONTENTS_VIEW_MODE", "1", domain="poipiku.com")

    def items(self):
        password = self.config("password", "")

        for post_url in self.posts():
            parts = post_url.split("/")
            if post_url[0] == "/":
                post_url = self.root + post_url
            page = self.request(post_url).text
            extr = text.extract_from(page)

            post = {
                "post_category": extr("<title>[", "]"),
                "count"      : text.parse_int(extr("(", " ")),
                "post_id"    : parts[-1].partition(".")[0],
                "user_id"    : parts[-2],
                "user_name"  : text.unescape(extr(
                    '<h2 class="UserInfoUserName">', '</').rpartition(">")[2]),
                "description": text.unescape(extr(
                    'class="IllustItemDesc" >', '</h1>')),
                "_http_headers": {"Referer": post_url},
            }

            yield Message.Directory, post
            post["num"] = warning = 0

            while True:
                thumb = extr('class="IllustItemThumbImg" src="', '"')
                if not thumb:
                    break
                elif thumb.startswith(("//img.poipiku.com/img/", "/img/")):
                    if "/warning" in thumb:
                        warning = True
                    self.log.debug("%s: %s", post["post_id"], thumb)
                    continue
                post["num"] += 1
                url = text.ensure_http_scheme(thumb[:-8]).replace(
                    "//img.", "//img-org.", 1)
                yield Message.Url, url, text.nameext_from_url(url, post)

            if not warning and not extr('ShowAppendFile', '<'):
                continue

            url = self.root + "/f/ShowAppendFileF.jsp"
            headers = {
                "Accept" : "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Origin" : self.root,
                "Referer": post_url,
            }
            data = {
                "UID": post["user_id"],
                "IID": post["post_id"],
                "PAS": password,
                "MD" : "0",
                "TWF": "-1",
            }
            resp = self.request(
                url, method="POST", headers=headers, data=data).json()

            page = resp["html"]
            if (resp.get("result_num") or 0) < 0:
                self.log.warning("%s: '%s'",
                                 post["post_id"], page.replace("<br/>", " "))

            for thumb in text.extract_iter(
                    page, 'class="IllustItemThumbImg" src="', '"'):
                post["num"] += 1
                url = text.ensure_http_scheme(thumb[:-8]).replace(
                    "//img.", "//img-org.", 1)
                yield Message.Url, url, text.nameext_from_url(url, post)


class PoipikuUserExtractor(PoipikuExtractor):
    """Extractor for posts from a poipiku user"""
    subcategory = "user"
    pattern = (BASE_PATTERN + r"/(?:IllustListPcV\.jsp\?PG=(\d+)&ID=)?"
               r"(\d+)/?(?:$|[?&#])")
    example = "https://poipiku.com/12345/"

    def __init__(self, match):
        PoipikuExtractor.__init__(self, match)
        self._page, self.user_id = match.groups()

    def posts(self):
        url = self.root + "/IllustListPcV.jsp"
        params = {
            "PG" : text.parse_int(self._page, 0),
            "ID" : self.user_id,
            "KWD": "",
        }

        while True:
            page = self.request(url, params=params).text

            cnt = 0
            for path in text.extract_iter(
                    page, 'class="IllustInfo" href="', '"'):
                yield path
                cnt += 1

            if cnt < 48:
                return
            params["PG"] += 1


class PoipikuPostExtractor(PoipikuExtractor):
    """Extractor for a poipiku post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(\d+)/(\d+)"
    example = "https://poipiku.com/12345/12345.html"

    def __init__(self, match):
        PoipikuExtractor.__init__(self, match)
        self.user_id, self.post_id = match.groups()

    def posts(self):
        return ("/{}/{}.html".format(self.user_id, self.post_id),)
