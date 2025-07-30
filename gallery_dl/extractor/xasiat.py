# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xasiat.com"""

from .common import Extractor, Message
from .. import text, util
import time

BASE_PATTERN = r"(?:https?://)?(?:www\.)?xasiat\.com((?:/fr|/ja)?/albums"


class XasiatExtractor(Extractor):
    category = "xasiat"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{album_url}_{num}"
    root = "https://www.xasiat.com"

    def items(self):
        data = {"_extractor": XasiatAlbumExtractor}
        for url in self.posts():
            yield Message.Queue, url, data

    def posts(self):
        return self._pagination(self.groups[0])

    def _pagination(self, path, pnum=1):
        url = f"{self.root}{path}/"
        find_posts = util.re(r'class="item  ">\s*<a href="([^"]+)').findall

        while True:
            params = {
                "mode": "async",
                "function": "get_block",
                "block_id": "list_albums_common_albums_list",
                "sort_by": "post_date",
                "from": pnum,
                "_": int(time.time() * 1000)
            }

            page = self.request(url, params=params).text
            yield from find_posts(page)

            if "<span>Next</span>" in page:
                return

            pnum += 1


class XasiatAlbumExtractor(XasiatExtractor):
    subcategory = "album"
    pattern = BASE_PATTERN + r"/\d+/[^/?#]+)"
    example = "https://www.xasiat.com/albums/12345/abc/"

    def items(self):
        url = self.root + self.groups[0] + "/"
        page = self.request(url).text
        images = text.extr(page, 'class="images">', "<div")
        urls = list(text.extract_iter(images, 'href="', '"'))

        data = {
            "title": text.unescape(text.extr(page, "<h1>", "</h1>")),
            "model": util.re(
                r'top_models1"></i>\s*(.+)\s*</span').findall(page),
            "tags": util.re(
                r'tags/[^"]+\">\s*(.+)\s*</a').findall(page),
            "album_category": util.re(
                r'categories/[^"]+\">\s*(.+)\s*</a').findall(page)[0],
            "album_url": text.unquote(url),
            "count": len(urls),
        }

        yield Message.Directory, data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url[:-1], data)


class XasiatTagExtractor(XasiatExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tags/[^/?#]+)"
    example = "https://www.xasiat.com/albums/tags/TAG/"


class XasiatCategoryExtractor(XasiatExtractor):
    subcategory = "category"
    pattern = BASE_PATTERN + r"/categories/[^/?#]+)"
    example = "https://www.xasiat.com/albums/categories/CATEGORY/"


class XasiatModelExtractor(XasiatExtractor):
    subcategory = "model"
    pattern = BASE_PATTERN + r"/models/[^/?#]+)"
    example = "https://www.xasiat.com/albums/models/MODEL/"
