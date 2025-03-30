# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://everia.club"""

from .common import Extractor, Message
from .. import text
import re

BASE_PATTERN = r"(?:https?://)?everia\.club"


class EveriaExtractor(Extractor):
    category = "everia"
    root = "https://everia.club"

    def items(self):
        data = {"_extractor": EveriaPostExtractor}
        for url in self.posts():
            yield Message.Queue, url, data

    def posts(self):
        return self._pagination(self.groups[0])

    def _pagination(self, path, params=None, pnum=1):
        find_posts = re.compile(r'thumbnail">\s*<a href="([^"]+)').findall

        while True:
            if pnum == 1:
                url = "{}{}/".format(self.root, path)
            else:
                url = "{}{}/page/{}/".format(self.root, path, pnum)
            response = self.request(url, params=params, allow_redirects=False)

            if response.status_code >= 300:
                return

            yield from find_posts(response.text)
            pnum += 1


class EveriaPostExtractor(EveriaExtractor):
    subcategory = "post"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{post_url}_{num}"
    pattern = BASE_PATTERN + r"(/\d{4}/\d{2}/\d{2}/[^/?#]+)"
    example = "https://everia.club/0000/00/00/TITLE"

    def items(self):
        url = self.root + self.groups[0]
        page = self.request(url).text
        content = text.extr(page, 'itemprop="text">', "<h3")
        urls = re.findall(r'img.*?src="([^"]+)', content)

        data = {
            "title": text.unescape(
                text.extr(page, 'itemprop="headline">', "</h1>")),
            "tags": list(text.extract_iter(page, 'rel="tag">', "</a>")),
            "post_url": url,
            "post_category": text.extr(
                page, "post-in-category-", " ").capitalize(),
            "count": len(urls),
        }

        yield Message.Directory, data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)


class EveriaTagExtractor(EveriaExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"(/tag/[^/?#]+)"
    example = "https://everia.club/tag/TAG"


class EveriaCategoryExtractor(EveriaExtractor):
    subcategory = "category"
    pattern = BASE_PATTERN + r"(/category/[^/?#]+)"
    example = "https://everia.club/category/CATEGORY"


class EveriaDateExtractor(EveriaExtractor):
    subcategory = "date"
    pattern = (BASE_PATTERN +
               r"(/\d{4}(?:/\d{2})?(?:/\d{2})?)(?:/page/\d+)?/?$")
    example = "https://everia.club/0000/00/00"


class EveriaSearchExtractor(EveriaExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/(?:page/\d+/)?\?s=([^&#]+)"
    example = "https://everia.club/?s=SEARCH"

    def posts(self):
        params = {"s": self.groups[0]}
        return self._pagination("", params)
