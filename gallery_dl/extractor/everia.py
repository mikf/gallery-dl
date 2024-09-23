# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://everia.club"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?everia\.club"


class EveriaPostExtractor(Extractor):
    category = "everia"
    subcategory = "post"
    root = "https://everia.club"
    pattern = BASE_PATTERN + r"/(\d{4}/\d{2}/\d{2}/[^/]+)/?"
    example = "https://everia.club/0000/00/00/TITLE"
    directory_fmt = ("{category}", "{title}")

    def __init__(self, match):
        super().__init__(match)
        self.url = match.group(0)

    def items(self):
        page = self.request(self.url).text
        content = text.extr(page, 'itemprop="text">', "</div>")
        urls = re.findall(r'img.*?src=\"(.+?)\"', content)

        data = {
            "title": text.unescape(
                text.extr(page, 'itemprop="headline">', "</h1>")
            ),
            "url": self.url,
            "tags": list(text.extract_iter(page, 'rel="tag">', "</a>")),
            "post_category": text.extr(
                page, "post-in-category-", " "
            ).capitalize(),
            "count": len(urls),
        }

        yield Message.Directory, data
        for data["num"], url in enumerate(urls, 1):
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data


class EveriaTagExtractor(EveriaPostExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/(tag/[^/]+)/?"
    example = "https://everia.club/tag/TAG"

    def __init__(self, match):
        super().__init__(match)
        self.id = match.group(1)

    def _posts(self, page):
        posts = re.findall(r'thumbnail\">\s*<a href=\"(.+?)\"', page)
        for post in posts:
            yield Message.Queue, post, {"_extractor": EveriaPostExtractor}

    def items(self):
        url = "{}/{}/".format(self.root, self.id)
        page = self.request(url).text
        yield from self._posts(page)
        pages = list(text.extract_iter(page, "/page/", "/"))
        if pages:
            for i in range(2, int(pages[-2]) + 1):
                url = "{}/{}/page/{}/".format(self.root, self.id, i + 1)
                page = self.request(url).text
                yield from self._posts(page)


class EveriaSearchExtractor(EveriaTagExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:page/\d+/)?\?s=(.+)"
    example = "https://everia.club/?s=SEARCH"

    def items(self):
        params = {"s": self.id}
        page = self.request(self.root, params=params).text
        yield from self._posts(page)
        pages = list(text.extract_iter(page, "/page/", "/"))
        if pages:
            for i in range(2, int(pages[-2]) + 1):
                url = "{}/page/{}/".format(self.root, i)
                page = self.request(url, params=params).text
                yield from self._posts(page)


class EveriaCategoryExtractor(EveriaTagExtractor):
    subcategory = "category"
    pattern = BASE_PATTERN + r"/(category/[^/]+)/?"
    example = "https://everia.club/category/CATEGORY"


class EveriaDateExtractor(EveriaTagExtractor):
    subcategory = "date"
    pattern = BASE_PATTERN + \
        r"/(\d{4}(?:/\d{2})?(?:/\d{2})?)(?:/page/\d+)?/?$"
    example = "https://everia.club/0000/00/00"
