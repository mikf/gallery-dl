# -*- coding: utf-8 -*-

# Copyright 2020-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.subscribestar.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?subscribestar\.(com|adult)"


class SubscribestarExtractor(Extractor):
    """Base class for subscribestar extractors"""
    category = "subscribestar"
    root = "https://www.subscribestar.com"
    directory_fmt = ("{category}", "{author_name}")
    filename_fmt = "{post_id}_{id}.{extension}"
    archive_fmt = "{id}"
    cookies_domain = "www.subscribestar.com"
    cookies_names = ("auth_token",)

    def __init__(self, match):
        tld, self.item = match.groups()
        if tld == "adult":
            self.root = "https://subscribestar.adult"
            self.cookies_domain = "subscribestar.adult"
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
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=28*86400, keyarg=1)
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

    def _media_from_post(self, html):
        media = []

        gallery = text.extr(html, 'data-gallery="', '"')
        if gallery:
            for item in util.json_loads(text.unescape(gallery)):
                if "/previews" in item["url"]:
                    self._warn_preview()
                else:
                    media.append(item)

        attachments = text.extr(
            html, 'class="uploads-docs"', 'data-role="post-edit_form"')
        if attachments:
            for att in attachments.split('class="doc_preview"')[1:]:
                media.append({
                    "id"  : text.parse_int(text.extr(
                        att, 'data-upload-id="', '"')),
                    "name": text.unescape(text.extr(
                        att, 'doc_preview-title">', '<')),
                    "url" : text.unescape(text.extr(att, 'href="', '"')),
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

    def _warn_preview(self):
        self.log.warning("Preview image detected")
        self._warn_preview = util.noop


class SubscribestarUserExtractor(SubscribestarExtractor):
    """Extractor for media from a subscribestar user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!posts/)([^/?#]+)"
    example = "https://www.subscribestar.com/USER"

    def posts(self):
        needle_next_page = 'data-role="infinite_scroll-next_page" href="'
        page = self.request("{}/{}".format(self.root, self.item)).text

        while True:
            posts = page.split('<div class="post ')[1:]
            if not posts:
                return
            yield from posts

            url = text.extr(posts[-1], needle_next_page, '"')
            if not url:
                return
            page = self.request(self.root + text.unescape(url)).json()["html"]


class SubscribestarPostExtractor(SubscribestarExtractor):
    """Extractor for media from a single subscribestar post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    example = "https://www.subscribestar.com/posts/12345"

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
                '<span class="star_link-types">', '<')),
            "content"    : (extr(
                '<div class="post-content', '<div class="post-uploads')
                .partition(">")[2]),
        }
