# -*- coding: utf-8 -*-

# Copyright 2020-2024 Mike Fährmann
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
                if item["url"][0] == "/":
                    item["url"] = self.root + item["url"]
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

    def _extract_media(self, html, media_types):
        media = []
        media_config = {
            "gallery": ('data-gallery="', '"', self._process_gallery_item),
            "attachments": (
                'class="uploads-docs"',
                'data-role="post-edit_form"',
                self._process_attachment_item,
            ),
            "link": ('data-href="', '"', self._process_media_item),
            "audio": ('<source src="', '" type="audio/',
                      self._process_media_item),
        }

        for key, config in media_types.items():
            if key in media_config:
                start, end, processor = media_config[key]
                segments = (
                    text.extract_all(
                        html,
                        ((key, start, end),),
                    )[0],
                )
                for segment in segments:
                    if segment[key]:
                        content = processor(segment, key)
                        if content:
                            media.append(content)
        return media

    def _process_gallery_item(self, item, media_type):
        gallery_list = util.json_loads(text.unescape(item["gallery"]))
        for media in gallery_list:
            if "/previews" in media["url"]:
                self._warn_preview()
            return {"url": media["url"], "type": media_type}

    def _process_attachment_item(self, item, media_type):
        return {
            "id": text.parse_int(text.extr(item, 'data-upload-id="', '"')),
            "name": text.unescape(text.extr(item, 'doc_preview-title">', "<")),
            "url": text.unescape(text.extr(item, 'href="', '"')),
            "type": media_type,
        }

    def _process_media_item(self, item, media_type):
        if media_type == "link" and util.check_if_supported_by_ytdlp(
                item[media_type]):
            return {"url": "ytdl:" + item[media_type], "type": media_type}
        elif media_type == "audio":
            return {"url": item[media_type], "type": media_type}

    def _media_from_post(self, html):
        media_types = {
            "gallery": True,
            "attachments": True,
            "link": True,
            "audio": True,
        }
        media = self._extract_media(html, media_types)
        return media

    def _data_from_post(self, html):
        extr = text.extract_from(html)

        links = (text.extract_all(html, (("url", 'data-href="', '"'),), )[0],)
        audios = (text.extract_all(html, (("url", '<source src="',
                                           '" type="audio/'),),)[0],)
        gallery = text.extr(html, 'data-gallery="', '"')

        content_type = None
        if links and any(item["url"] for item in links):
            content_type = "link"
        if audios and any(item["url"] for item in audios):
            content_type = "audio"
        if gallery:
            for item in util.json_loads(text.unescape(gallery)):
                if item["type"] == "video":
                    content_type = "video"
                    break
                else:
                    content_type = "image"

        return {
            "post_id"      : text.parse_int(extr('data-id="', '"')),
            "author_id"    : text.parse_int(extr('data-user-id="', '"')),
            "author_name"  : text.unescape(extr('href="/', '"')),
            "author_nick"  : text.unescape(extr(">", "<")),
            "date"         : self._parse_datetime(
                extr('class="post-date">', "</").rpartition(">")[2]),
            "content"      : extr("<body>\n", "\n</body>"),
            "content_type" : content_type,
        }

    def _parse_datetime(self, dt):
        if dt.startswith("Updated on "):
            dt = dt[11:]
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
