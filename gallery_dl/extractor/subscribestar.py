# -*- coding: utf-8 -*-

# Copyright 2020-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.subscribestar.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import json

BASE_PATTERN = r"(?:https?://)?(?:www\.)?subscribestar\.(com|adult)"


class SubscribestarExtractor(Extractor):
    """Base class for subscribestar extractors"""
    category = "subscribestar"
    root = "https://www.subscribestar.com"
    directory_fmt = ("{category}", "{author_name}")
    filename_fmt = "{post_id}_{id}.{extension}"
    archive_fmt = "{id}"
    cookiedomain = "www.subscribestar.com"
    cookienames = ("auth_token",)

    def __init__(self, match):
        tld, self.item = match.groups()
        if tld == "adult":
            self.root = "https://subscribestar.adult"
            self.cookiedomain = "subscribestar.adult"
            self.subcategory += "-adult"
        Extractor.__init__(self, match)

    def items(self):
        self.login()
        for post_html in self.posts():
            media = self._media_from_post(post_html)
            data = self._data_from_post(post_html)
            yield Message.Directory, data
            for num, item in enumerate(media, 1):
                item.update(data)
                item["num"] = num
                text.nameext_from_url(item.get("name") or item["url"], item)
                yield Message.Url, item["url"], item

    def posts(self):
        """Yield HTML content of all relevant posts"""

    def login(self):
        if self._check_cookies(self.cookienames):
            return
        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl(username, password)
            self._update_cookies(cookies)

    @cache(maxage=28*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://www.subscribestar.com/session.json"
        headers = {
            "Origin"          : "https://www.subscribestar.com",
            "Referer"         : "https://www.subscribestar.com/login",
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {
            "utf8"    : "✓",
            "email"   : username,
            "password": password,
        }

        response = self.request(
            url, method="POST", headers=headers, data=data, fatal=False)
        if response.json().get("errors"):
            self.log.debug(response.json()["errors"])
            raise exception.AuthenticationError()

        return {
            cookie.name: cookie.value
            for cookie in response.cookies
            if cookie.name.startswith("auth")
        }

    @staticmethod
    def _media_from_post(html):
        media = []

        gallery = text.extract(html, 'data-gallery="', '"')[0]
        if gallery:
            media.extend(
                item for item in json.loads(text.unescape(gallery))
                if "/previews/" not in item["url"]
            )

        attachments = text.extract(
            html, 'class="uploads-docs"', 'data-role="post-edit_form"')[0]
        if attachments:
            for att in attachments.split('class="doc_preview"')[1:]:
                media.append({
                    "id"  : text.parse_int(text.extract(
                        att, 'data-upload-id="', '"')[0]),
                    "name": text.unescape(text.extract(
                        att, 'doc_preview-title">', '<')[0] or ""),
                    "url" : text.unescape(text.extract(att, 'href="', '"')[0]),
                    "type": "attachment",
                })

        return media

    def _data_from_post(self, html):
        extr = text.extract_from(html)
        return {
            "post_id"    : text.parse_int(extr('data-id="', '"')),
            "author_id"  : text.parse_int(extr('data-user-id="', '"')),
            "author_name": text.unescape(extr('href="/', '"')),
            "author_nick": text.unescape(extr('>', '<')),
            "date"       : self._parse_datetime(extr(
                'class="post-date">', '</').rpartition(">")[2]),
            "content"    : (extr(
                '<div class="post-content', '<div class="post-uploads')
                .partition(">")[2]),
        }

    def _parse_datetime(self, dt):
        date = text.parse_datetime(dt, "%b %d, %Y %I:%M %p")
        if date is dt:
            date = text.parse_datetime(dt, "%B %d, %Y %I:%M %p")
        return date


class SubscribestarUserExtractor(SubscribestarExtractor):
    """Extractor for media from a subscribestar user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!posts/)([^/?#]+)"
    test = (
        ("https://www.subscribestar.com/subscribestar", {
            "count": ">= 20",
            "pattern": r"https://\w+\.cloudfront\.net/uploads(_v2)?/users/11/",
            "keyword": {
                "author_id": 11,
                "author_name": "subscribestar",
                "author_nick": "SubscribeStar",
                "content": str,
                "date"   : "type:datetime",
                "id"     : int,
                "num"    : int,
                "post_id": int,
                "type"   : "re:image|video|attachment",
                "url"    : str,
                "?pinned": bool,
            },
        }),
        ("https://www.subscribestar.com/subscribestar", {
            "options": (("metadata", True),),
            "keyword": {"date": "type:datetime"},
            "range": "1",
        }),
        ("https://subscribestar.adult/kanashiipanda", {
            "range": "1-10",
            "count": 10,
        }),
    )

    def posts(self):
        needle_next_page = 'data-role="infinite_scroll-next_page" href="'
        page = self.request("{}/{}".format(self.root, self.item)).text

        while True:
            posts = page.split('<div class="post ')[1:]
            if not posts:
                return
            yield from posts

            url = text.extract(posts[-1], needle_next_page, '"')[0]
            if not url:
                return
            page = self.request(self.root + text.unescape(url)).json()["html"]


class SubscribestarPostExtractor(SubscribestarExtractor):
    """Extractor for media from a single subscribestar post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = (
        ("https://www.subscribestar.com/posts/102468", {
            "count": 1,
            "keyword": {
                "author_id": 11,
                "author_name": "subscribestar",
                "author_nick": "SubscribeStar",
                "content": "re:<h1>Brand Guidelines and Assets</h1>",
                "date": "dt:2020-05-07 12:33:00",
                "extension": "jpg",
                "filename": "8ff61299-b249-47dc-880a-cdacc9081c62",
                "group": "imgs_and_videos",
                "height": 291,
                "id": 203885,
                "num": 1,
                "pinned": False,
                "post_id": 102468,
                "type": "image",
                "width": 700,
            },
        }),
        ("https://subscribestar.adult/posts/22950", {
            "count": 1,
            "keyword": {"date": "dt:2019-04-28 07:32:00"},
        }),
    )

    def posts(self):
        url = "{}/posts/{}".format(self.root, self.item)
        return (self.request(url).text,)

    def _data_from_post(self, html):
        extr = text.extract_from(html)
        return {
            "post_id"    : text.parse_int(extr('data-id="', '"')),
            "author_name": text.unescape(extr('href="/', '"')),
            "author_id"  : text.parse_int(extr('data-user-id="', '"')),
            "author_nick": text.unescape(extr('alt="', '"')),
            "date"       : self._parse_datetime(extr(
                'class="section-subtitle">', '<')),
            "content"    : (extr(
                '<div class="post-content', '<div class="post-uploads')
                .partition(">")[2]),
        }
