# -*- coding: utf-8 -*-

# Copyright 2020-2025 Mike Fährmann
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
    cookies_domain = ".subscribestar.com"
    cookies_names = ("_personalization_id",)
    _warning = True

    def __init__(self, match):
        tld, self.item = match.groups()
        if tld == "adult":
            self.root = "https://subscribestar.adult"
            self.cookies_domain = ".subscribestar.adult"
            self.subcategory += "-adult"
        Extractor.__init__(self, match)

    def items(self):
        self.login()
        for post_html in self.posts():
            media = self._media_from_post(post_html)
            data = self._data_from_post(post_html)

            content = data["content"]
            if "<html><body>" in content:
                data["content"] = content = text.extr(
                    content, "<body>", "</body>")
            data["title"] = text.unescape(text.rextr(content, "<h1>", "</h1>"))

            yield Message.Directory, "", data
            for num, item in enumerate(media, 1):
                item.update(data)
                item["num"] = num

                url = item["url"]
                if name := (item.get("name") or item.get("original_filename")):
                    text.nameext_from_name(name, item)
                else:
                    text.nameext_from_url(url, item)

                if url[0] == "/":
                    url = f"{self.root}{url}"
                yield Message.Url, url, item

    def posts(self):
        """Yield HTML content of all relevant posts"""

    def request(self, url, **kwargs):
        while True:
            response = Extractor.request(self, url, **kwargs)

            if response.history and (
                    "/verify_subscriber" in response.url or
                    "/age_confirmation_warning" in response.url):
                raise exception.AbortExtraction(
                    f"HTTP redirect to {response.url}")

            content = response.content
            if len(content) < 250 and b">redirected<" in content:
                url = text.unescape(text.extr(
                    content, b'href="', b'"').decode())
                self.log.debug("HTML redirect message for %s", url)
                continue

            return response

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(
                (username, self.cookies_domain), password))

        if self._warning:
            if not username or not self.cookies_check(self.cookies_names):
                self.log.warning("no '_personalization_id' cookie set")
            SubscribestarExtractor._warning = False

    @cache(maxage=28*86400, keyarg=1)
    def _login_impl(self, username, password):
        username = username[0]
        self.log.info("Logging in as %s", username)

        if self.root.endswith(".adult"):
            self.cookies.set("18_plus_agreement_generic", "true",
                             domain=self.cookies_domain)

        # load login page
        url = self.root + "/login"
        page = self.request(url).text

        headers = {
            "Accept": "*/*;q=0.5, text/javascript, application/javascript, "
                      "application/ecmascript, application/x-ecmascript",
            "Referer": self.root + "/login",
            "X-CSRF-Token": text.unescape(text.extr(
                page, '<meta name="csrf-token" content="', '"')),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }

        def check_errors(response):
            if errors := response.json().get("errors"):
                self.log.debug(errors)
                try:
                    msg = f'"{errors.popitem()[1]}"'
                except Exception:
                    msg = None
                raise exception.AuthenticationError(msg)
            return response

        # submit username / email
        url = self.root + "/session.json"
        data = {"email": username}
        response = check_errors(self.request(
            url, method="POST", headers=headers, data=data, fatal=False))

        # submit password
        url = self.root + "/session/password.json"
        data = {"password": password}
        response = check_errors(self.request(
            url, method="POST", headers=headers, data=data, fatal=False))

        # return cookies
        return {
            cookie.name: cookie.value
            for cookie in response.cookies
        }

    def _media_from_post(self, html):
        media = []

        if gallery := text.extr(html, 'data-gallery="', '"'):
            for item in util.json_loads(text.unescape(gallery)):
                if "/previews" in item["url"]:
                    self._warn_preview()
                else:
                    media.append(item)

        attachments = text.extr(
            html, 'class="uploads-docs"', 'class="post-edit_form"')
        if attachments:
            for att in text.re(r'class="doc_preview[" ]').split(
                    attachments)[1:]:
                media.append({
                    "id"  : text.parse_int(text.extr(
                        att, 'data-upload-id="', '"')),
                    "name": text.unescape(text.extr(
                        att, 'doc_preview-title">', '<')),
                    "url" : text.unescape(text.extr(att, 'href="', '"')),
                    "type": "attachment",
                })

        audios = text.extr(
            html, 'class="uploads-audios"', 'class="post-edit_form"')
        if audios:
            for audio in text.re(r'class="audio_preview-data[" ]').split(
                    audios)[1:]:
                media.append({
                    "id"  : text.parse_int(text.extr(
                        audio, 'data-upload-id="', '"')),
                    "name": text.unescape(text.extr(
                        audio, 'audio_preview-title">', '<')),
                    "url" : text.unescape(text.extr(audio, 'src="', '"')),
                    "type": "audio",
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
            "content"    : extr(
                '<div class="post-content" data-role="post_content-text">',
                '</div><div class="post-uploads for-youtube"').strip(),
            "tags"       : list(text.extract_iter(extr(
                '<div class="post_tags for-post">',
                '<div class="post-actions">'), '?tag=', '"')),
        }

    def _parse_datetime(self, dt):
        if dt.startswith("Updated on "):
            dt = dt[11:]
        date = self.parse_datetime(dt, "%b %d, %Y %I:%M %p")
        if date is dt:
            date = self.parse_datetime(dt, "%B %d, %Y %I:%M %p")
        return date

    def _warn_preview(self):
        self.log.warning("Preview image detected")
        self._warn_preview = util.noop


class SubscribestarUserExtractor(SubscribestarExtractor):
    """Extractor for media from a subscribestar user"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/(?!posts/)([^/?#]+)"
    example = "https://www.subscribestar.com/USER"

    def posts(self):
        needle_next_page = 'data-role="infinite_scroll-next_page" href="'
        page = self.request(f"{self.root}/{self.item}").text

        while True:
            posts = page.split('<div class="post ')[1:]
            if not posts:
                return
            yield from posts

            url = text.extr(posts[-1], needle_next_page, '"')
            if not url:
                return
            page = self.request_json(self.root + text.unescape(url))["html"]


class SubscribestarPostExtractor(SubscribestarExtractor):
    """Extractor for media from a single subscribestar post"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/posts/(\d+)"
    example = "https://www.subscribestar.com/posts/12345"

    def posts(self):
        url = f"{self.root}/posts/{self.item}"
        return (self.request(url).text,)

    def _data_from_post(self, html):
        extr = text.extract_from(html)
        return {
            "post_id"    : text.parse_int(extr('data-id="', '"')),
            "date"       : self._parse_datetime(extr(
                '<div class="section-title_date">', '<')),
            "content"    : extr(
                '<div class="post-content" data-role="post_content-text">',
                '</div><div class="post-uploads for-youtube"').strip(),
            "tags"       : list(text.extract_iter(extr(
                '<div class="post_tags for-post">',
                '<div class="post-actions">'), '?tag=', '"')),
            "author_name": text.unescape(extr(
                'class="star_link" href="/', '"')),
            "author_id"  : text.parse_int(extr('data-user-id="', '"')),
            "author_nick": text.unescape(extr('alt="', '"')),
        }
