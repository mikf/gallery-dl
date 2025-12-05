# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xasiat.com"""

from .common import Extractor, Message
from .. import text
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
        find_posts = text.re(r'class="item  ">\s*<a href="([^"]+)').findall

        while True:
            params = {
                "mode": "async",
                "function": "get_block",
                "block_id": "list_albums_common_albums_list",
                "sort_by": "post_date",
                "from": pnum,
                "_": int(time.time() * 1000),
            }

            page = self.request(url, params=params).text
            yield from find_posts(page)

            if "<span>Next</span>" in page:
                return

            pnum += 1


class XasiatAlbumExtractor(XasiatExtractor):
    subcategory = "album"
    pattern = rf"{BASE_PATTERN}/(\d+)/[^/?#]+)"
    example = "https://www.xasiat.com/albums/12345/TITLE/"

    def items(self):
        path, album_id = self.groups
        url = f"{self.root}{path}/"
        response = self.request(url)
        extr = text.extract_from(response.text)

        title = extr("<h1>", "<")
        info = extr('class="info-content"', "</div>")
        images = extr('class="images"', "</div>")

        urls = list(text.extract_iter(images, 'href="', '"'))
        categories = text.re(r'categories/[^"]+\">\s*(.+)\s*</a').findall(info)
        data = {
            "title": text.unescape(title),
            "model": text.re(
                r'top_models1"></i>\s*(.+)\s*</span').findall(info),
            "tags": text.re(
                r'tags/[^"]+\">\s*(.+)\s*</a').findall(info),
            "album_category": categories[0] if categories else "",
            "album_url": response.url,
            "album_id": text.parse_int(album_id),
            "count": len(urls),
        }

        yield Message.Directory, "", data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url[:-1], data)


class XasiatTagExtractor(XasiatExtractor):
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}/tags/[^/?#]+)"
    example = "https://www.xasiat.com/albums/tags/TAG/"


class XasiatCategoryExtractor(XasiatExtractor):
    subcategory = "category"
    pattern = rf"{BASE_PATTERN}/categories/[^/?#]+)"
    example = "https://www.xasiat.com/albums/categories/CATEGORY/"


class XasiatModelExtractor(XasiatExtractor):
    subcategory = "model"
    pattern = rf"{BASE_PATTERN}/models/[^/?#]+)"
    example = "https://www.xasiat.com/albums/models/MODEL/"
