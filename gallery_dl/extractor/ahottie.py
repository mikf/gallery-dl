# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://ahottie.top/"""

from .common import Extractor, GalleryExtractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?ahottie\.top"


class AhottieExtractor(Extractor):
    """Base class for ahottie extractors"""
    category = "ahottie"
    root = "https://ahottie.top"

    def items(self):
        for album in self.albums():
            yield Message.Queue, album["url"], album

    def _pagination(self, url, params):
        params["page"] = text.parse_int(params.get("page"), 1)

        while True:
            page = self.request(url, params=params).text

            for album in text.extract_iter(
                    page, '<div class="relative">', '</div>'):
                yield {
                    "url"  : text.extr(album, ' href="', '"'),
                    "title": text.unquote(text.extr(
                        album, ' alt="', '"')),
                    "date" : self.parse_datetime_iso(text.extr(
                        album, ' datetime="', '"')),
                    "_extractor": AhottieGalleryExtractor,
                }

            if 'rel="next"' not in page:
                break
            params["page"] += 1


class AhottieGalleryExtractor(GalleryExtractor, AhottieExtractor):
    directory_fmt = ("{category}", "{date:%Y-%m-%d} {title} ({gallery_id})")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{gallery_id}_{num}_{filename}"
    pattern = BASE_PATTERN + r"(/albums/(\w+))"
    example = "https://ahottie.top/albums/1234567890"

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "gallery_id": self.groups[1],
            "title": text.unescape(extr("<title>", "<").rpartition(" | ")[0]),
            "date" : self.parse_datetime_iso(extr('datetime="', '"')),
            "tags" : text.split_html(extr('<i ', '</div>'))[1:],
        }

    def images(self, page):
        data = {
            "_http_headers" : {"Referer": None},
            "_http_validate": self._validate,
        }

        results = []
        while True:
            pos = page.find("<time ") + 1
            for url in text.extract_iter(page, '" src="', '"', pos):
                results.append((url, data))

            pos = page.find('rel="next"', pos)
            if pos < 0:
                break
            page = self.request(text.rextr(page, 'href="', '"', pos)).text
        return results

    def _validate(self, response):
        hget = response.headers.get
        return not (
            hget("content-length") == "2421" and
            hget("content-type") == "image/jpeg"
        )


class AhottieTagExtractor(AhottieExtractor):
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tags/([^/?#]+)"
    example = "https://ahottie.top/tags/TAG"

    def albums(self):
        tag = self.groups[0]
        self.kwdict["search_tags"] = text.unquote(tag)
        return self._pagination(f"{self.root}/tags/{tag}", {})


class AhottieSearchExtractor(AhottieExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?([^#]+)"
    example = "https://ahottie.top/search?kw=QUERY"

    def albums(self):
        params = text.parse_query(self.groups[0])
        self.kwdict["search_tags"] = params.get("kw")
        return self._pagination(f"{self.root}/search", params)
