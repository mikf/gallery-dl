# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
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
                "count"      : extr("(", " "),
                "post_id"    : parts[-1].partition(".")[0],
                "user_id"    : parts[-2],
                "user_name"  : text.unescape(extr(
                    '<h2 class="UserInfoUserName">', '</').rpartition(">")[2]),
                "description": text.unescape(extr(
                    'class="IllustItemDesc" >', '<')),
                "_http_headers": {"Referer": post_url},
            }

            yield Message.Directory, post
            post["num"] = 0

            while True:
                thumb = extr('class="IllustItemThumbImg" src="', '"')
                if not thumb:
                    break
                elif thumb.startswith(("//img.poipiku.com/img/", "/img/")):
                    continue
                post["num"] += 1
                url = text.ensure_http_scheme(thumb[:-8]).replace(
                    "//img.", "//img-org.", 1)
                yield Message.Url, url, text.nameext_from_url(url, post)

            if not extr('> show all', '<'):
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
            page = self.request(
                url, method="POST", headers=headers, data=data).json()["html"]

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
    test = (
        ("https://poipiku.com/25049/", {
            "pattern": r"https://img-org\.poipiku\.com/user_img\d+/000025049"
                       r"/\d+_\w+\.(jpe?g|png)$",
            "range": "1-10",
            "count": 10,
        }),
        ("https://poipiku.com/IllustListPcV.jsp?PG=1&ID=25049&KWD=")
    )

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
    test = (
        ("https://poipiku.com/25049/5864576.html", {
            "pattern": r"https://img-org\.poipiku\.com/user_img\d+/000025049"
                       r"/005864576_EWN1Y65gQ\.png$",
            "keyword": {
                "count": "1",
                "description": "",
                "extension": "png",
                "filename": "005864576_EWN1Y65gQ",
                "num": 1,
                "post_category": "DOODLE",
                "post_id": "5864576",
                "user_id": "25049",
                "user_name": "ユキウサギ",
            },
        }),
        ("https://poipiku.com/2166245/6411749.html", {
            "pattern": r"https://img-org\.poipiku\.com/user_img\d+/002166245"
                       r"/006411749_\w+\.jpeg$",
            "count": 4,
            "keyword": {
                "count": "4",
                "description": "絵茶の産物ネタバレあるやつ",
                "num": int,
                "post_category": "SPOILER",
                "post_id": "6411749",
                "user_id": "2166245",
                "user_name": "wadahito",
            },
        }),
    )

    def __init__(self, match):
        PoipikuExtractor.__init__(self, match)
        self.user_id, self.post_id = match.groups()

    def posts(self):
        return ("/{}/{}.html".format(self.user_id, self.post_id),)
