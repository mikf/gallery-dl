# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.xasiat.com"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?xasiat\.com"


class XasiatExtractor(Extractor):
    category = "xasiat"
    root = "https://www.xasiat.com"

    def items(self):
        data = {"_extractor": XasiatAlbumExtractor}
        for url in self.posts():
            yield Message.Queue, url, data

    def posts(self):
        return self._pagination(self.groups[0])

    def _pagination(self, path, params=None, pnum=1):
        find_posts = util.re(r'thumbnail">\s*<a href="([^"]+)').findall

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


class XasiatAlbumExtractor(XasiatExtractor):
    subcategory = "album"
    directory_fmt = ("{category}", "{title}")
    archive_fmt = "{album_url}_{num}"
    pattern = BASE_PATTERN + r"(/albums/\d+/[^/?#]+)"
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
                r"tags/[^\"]+\">\s*(.+)\s*</a").findall(page),
            "album_category": util.re(
                r"categories/[^\"]+\">\s*(.+)\s*</a").findall(page),
            "album_url": text.unquote(url),
            "count": len(urls),
        }

        yield Message.Directory, data
        for data["num"], url in enumerate(urls, 1):
            yield Message.Url, url, text.nameext_from_url(url[:-1], data)
