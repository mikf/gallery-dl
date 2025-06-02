# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
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

    def items(self):
        self.__cookies = True
        for album_id in self.albums():
            url = "{}/a/{}".format(self.root, album_id)

            try:
                page = self.request(url).text
            except exception.HttpError as exc:
                self.log.warning(
                    "Unable to fetch album '%s' (%s)", album_id, exc)
                continue

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
                        date = text.parse_timestamp(ts)

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

            yield Message.Directory, data
            for data["num"], url in enumerate(urls, 1):
                yield Message.Url, url, text.nameext_from_url(url, data)

    def albums(self):
        return ()

    def request(self, url, **kwargs):
        if self.__cookies:
            self.__cookies = False
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
        for params["page"] in itertools.count(1):
            page = self.request(url, params=params).text

            album_ids = EromeAlbumExtractor.pattern.findall(page)[::2]
            yield from album_ids

            if len(album_ids) < 36:
                return


class EromeAlbumExtractor(EromeExtractor):
    """Extractor for albums on erome.com"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"/a/(\w+)"
    example = "https://www.erome.com/a/ID"

    def albums(self):
        return (self.groups[0],)


class EromeUserExtractor(EromeExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!a/|search\?)([^/?#]+)"
    example = "https://www.erome.com/USER"

    def albums(self):
        url = "{}/{}".format(self.root, self.groups[0])
        return self._pagination(url, {})


class EromeSearchExtractor(EromeExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?(q=[^#]+)"
    example = "https://www.erome.com/search?q=QUERY"

    def albums(self):
        url = self.root + "/search"
        params = text.parse_query(self.groups[0])
        return self._pagination(url, params)


@cache()
def _cookie_cache():
    return ()
