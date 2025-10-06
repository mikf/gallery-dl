# -*- coding: utf-8 -*-

# Copyright 2022-2025 Mike Fährmann
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
    cookies_domain = "poipiku.com"
    cookies_warning = True
    request_interval = (0.5, 1.5)

    def _init(self):
        self.cookies.set(
            "LANG", "en", domain=self.cookies_domain)
        self.cookies.set(
            "POIPIKU_CONTENTS_VIEW_MODE", "1", domain=self.cookies_domain)
        self.headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Origin" : self.root,
            "Referer": None,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        self.password = self.config("password", "")

    def items(self):
        if self.cookies_check(("POIPIKU_LK",)):
            extract_files = self._extract_files_auth
            original = True
        else:
            extract_files = self._extract_files_noauth
            original = False
            if self.cookies_warning:
                self.log.warning("no 'POIPIKU_LK' cookie set")
                PoipikuExtractor.cookies_warning = False

        for post_url in self.posts():
            if post_url[0] == "/":
                post_url = f"{self.root}{post_url}"
            self.headers["Referer"] = post_url

            page = self.request(post_url).text
            extr = text.extract_from(page)
            parts = post_url.rsplit("/", 2)
            post = {
                "post_category": extr("<title>[", "]"),
                "count"      : text.parse_int(extr("(", " ")),
                "post_id"    : parts[2].partition(".")[0],
                "user_id"    : parts[1],
                "user_name"  : text.unescape(extr(
                    '<h2 class="UserInfoUserName">', '</').rpartition(">")[2]),
                "description": text.unescape(extr(
                    'class="IllustItemDesc" >', '</h1>')),
                "original"   : original,
                "_http_headers": {"Referer": post_url},
            }

            yield Message.Directory, post
            for post["num"], url in enumerate(extract_files(post, extr), 1):
                yield Message.Url, url, text.nameext_from_url(url, post)

    def _extract_files_auth(self, post, _):
        url = f"{self.root}/f/ShowIllustDetailF.jsp"
        data = {
            "ID" : post["user_id"],
            "TD" : post["post_id"],
            "AD" : "-1",
            "PAS": self.password,
        }
        resp = self.request_json(
            url, method="POST", headers=self.headers, data=data)

        html = resp["html"]
        if (resp.get("result_num") or 0) < 0:
            self.log.warning("%s: '%s'",
                             post["post_id"], html.replace("<br/>", " "))
        return text.extract_iter(html, 'src="', '"')

    def _extract_files_noauth(self, post, extr):
        files = []
        warning = False

        while True:
            thumb = extr('class="IllustItemThumbImg" src="', '"')
            if not thumb:
                break
            if thumb.startswith((
                "https://img.poipiku.com/img/",
                "//img.poipiku.com/img/",
                "/img/",
            )):
                if "/warning" in thumb:
                    warning = True
                self.log.debug("%s: %s", post["post_id"], thumb)
                continue
            files.append(thumb)

        if not warning and not extr('ShowAppendFile', '<'):
            return files

        url = f"{self.root}/f/ShowAppendFileF.jsp"
        data = {
            "UID": post["user_id"],
            "IID": post["post_id"],
            "PAS": self.password,
            "MD" : "0",
            "TWF": "-1",
        }
        resp = self.request_json(
            url, method="POST", headers=self.headers, data=data)

        html = resp["html"]
        if (resp.get("result_num") or 0) < 0:
            self.log.warning("%s: '%s'",
                             post["post_id"], html.replace("<br/>", " "))

        files.extend(text.extract_iter(
            html, 'class="IllustItemThumbImg" src="', '"'))
        return files


class PoipikuUserExtractor(PoipikuExtractor):
    """Extractor for posts from a poipiku user"""
    subcategory = "user"
    pattern = (rf"{BASE_PATTERN}/(?:IllustListPcV\.jsp\?PG=(\d+)&ID=)?"
               rf"(\d+)/?(?:$|[?&#])")
    example = "https://poipiku.com/12345/"

    def posts(self):
        pnum, user_id = self.groups

        url = f"{self.root}/IllustListPcV.jsp"
        params = {
            "PG" : text.parse_int(pnum, 0),
            "ID" : user_id,
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
    pattern = rf"{BASE_PATTERN}/(\d+)/(\d+)"
    example = "https://poipiku.com/12345/12345.html"

    def posts(self):
        user_id, post_id = self.groups
        return (f"/{user_id}/{post_id}.html",)
