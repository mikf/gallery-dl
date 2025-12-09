# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.erome.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?erome\.com"


class EromeExtractor(Extractor):
    category = "erome"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{album_id} {title} {num:>02}.{extension}"
    archive_fmt = "{album_id}_{num}"
    root = "https://www.erome.com"
    _cookies = True

    def items(self):
        base = f"{self.root}/a/"
        data = {"_extractor": EromeAlbumExtractor}
        for album_id in self.albums():
            yield Message.Queue, f"{base}{album_id}", data

    def albums(self):
        return ()

    def request(self, url, **kwargs):
        if self._cookies:
            self._cookies = False
            self.cookies.update(_cookie_cache())

        for _ in range(5):
            response = Extractor.request(self, url, **kwargs)
            if response.cookies:
                _cookie_cache.update("", response.cookies)
            if response.content.find(
                    b"<title>Please wait a few moments</title>", 0, 600) < 0:
                return response
            self.sleep(5.0, "check")

    def _pagination(self, url, params):
        find_albums = EromeAlbumExtractor.pattern.findall

        for params["page"] in itertools.count(
                text.parse_int(params.get("page"), 1)):
            page = self.request(url, params=params).text

            album_ids = find_albums(page)[::2]
            yield from album_ids

            if len(album_ids) < 36:
                return


class EromeAlbumExtractor(EromeExtractor):
    """Extractor for albums on erome.com"""
    subcategory = "album"
    pattern = rf"{BASE_PATTERN}/a/(\w+)"
    example = "https://www.erome.com/a/ID"

    def items(self):
        album_id = self.groups[0]
        url = f"{self.root}/a/{album_id}"

        try:
            page = self.request(url).text
        except exception.HttpError as exc:
            if exc.status == 410:
                msg = text.extr(exc.response.text, "<h1>", "<")
            else:
                msg = "Unable to fetch album page"
            raise exception.AbortExtraction(
                f"{album_id}: {msg} ({exc})")

        title, pos = text.extract(
            page, 'property="og:title" content="', '"')
        pos = page.index('<div class="user-profile', pos)
        user, pos = text.extract(
            page, 'href="https://www.erome.com/', '"', pos)
        tags, pos = text.extract(
            page, '<p class="mt-10"', '</p>', pos)

        urls = []
        date = None
        groups = page.split('<div class="media-group"')
        for group in util.advance(groups, 1):
            url = (text.extr(group, '<source src="', '"') or
                   text.extr(group, 'data-src="', '"'))
            if url:
                urls.append(url)
            if not date:
                ts = text.extr(group, '?v=', '"')
                if len(ts) > 1:
                    date = self.parse_timestamp(ts)

        data = {
            "album_id": album_id,
            "title"   : text.unescape(title),
            "user"    : text.unquote(user),
            "count"   : len(urls),
            "date"    : date,
            "tags"    : ([t.replace("+", " ")
                          for t in text.extract_iter(tags, "?q=", '"')]
                         if tags else ()),
            "_http_headers": {"Referer": url},
        }

        yield Message.Directory, "", data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)


class EromeUserExtractor(EromeExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/(?!a/|search\?)([^/?#]+)(?:/?\?([^#]+))?"
    example = "https://www.erome.com/USER"

    def albums(self):
        user, qs = self.groups
        url = f"{self.root}/{user}"

        params = text.parse_query(qs)
        if "t" not in params and not self.config("reposts", False):
            params["t"] = "posts"

        return self._pagination(url, params)


class EromeSearchExtractor(EromeExtractor):
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search/?\?(q=[^#]+)"
    example = "https://www.erome.com/search?q=QUERY"

    def albums(self):
        url = f"{self.root}/search"
        params = text.parse_query(self.groups[0])
        return self._pagination(url, params)


@cache()
def _cookie_cache():
    return ()
