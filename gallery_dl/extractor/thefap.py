# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://thefap.com/"""

from .common import Extractor, Message
from .. import text, exception


BASE_PATTERN = r"(?:https?://)?(?:www\.)?thefap\.(?:com|net)"


class ThefapExtractor(Extractor):
    """Base class for thefap extractors"""
    category = "thefap"
    root = "https://thefap.com"
    directory_fmt = ("{category}", "{model}")
    filename_fmt = "{model}_{num}.{extension}"

    def _extract_images(self, page, seen):
        section = text.extr(page, '<div id="content"', '<div id="showmore"')
        if not section:
            section = page

        for url in text.extract_iter(section, 'data-src="', '"'):
            url = self._normalize_url(url)
            if self._valid_image_url(url, seen):
                seen.add(url)
                yield url

        for url in text.extract_iter(section, 'src="', '"'):
            url = self._normalize_url(url)
            if self._valid_image_url(url, seen):
                seen.add(url)
                yield url

    def _valid_image_url(self, url, seen):
        if not url or url in seen:
            return False
        if "/assets/" in url or "blank.gif" in url:
            return False
        return True

    def _normalize_url(self, url):
        if not url:
            return ""
        url = url.strip()
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            return self.root + url
        return url


class ThefapModelExtractor(ThefapExtractor):
    """Extractor for model pages on thefap.com"""
    subcategory = "model"
    pattern = BASE_PATTERN + r"/([^/?#]+)-(\d+)(?:/)?$"
    example = "https://thefap.com/zoey.curly-374261/"

    def __init__(self, match):
        ThefapExtractor.__init__(self, match)
        self.root = text.root_from_url(match[0])
        self.model, self.model_id = match.groups()

    def items(self):
        base = f"{self.root}/{self.model}-{self.model_id}/"
        page = self.request(base).text
        if 'id="content"' not in page:
            raise exception.NotFoundError("model")

        model_name = text.remove_html(text.extr(page, "<h2", "</h2>"))
        if not model_name:
            model_name = text.unquote(self.model).replace(".", " ")

        data = {
            "model": self.model,
            "model_id": text.parse_int(self.model_id),
            "model_name": model_name,
        }
        yield Message.Directory, "", data

        seen = set()
        num = 0

        for url in self._extract_images(page, seen):
            num += 1
            data["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, data)

        pnum = 2
        while True:
            page_data = self._request_ajax(pnum)
            if not page_data:
                return

            added = 0
            for url in self._extract_images(page_data, seen):
                num += 1
                added += 1
                data["num"] = num
                yield Message.Url, url, text.nameext_from_url(url, data)

            if added == 0:
                return
            pnum += 1

    def _request_ajax(self, pnum):
        url = f"{self.root}/ajax/model/{self.model_id}/page-{pnum}"
        headers = {"X-Requested-With": "XMLHttpRequest"}
        return self.request(url, headers=headers).text


class ThefapItemExtractor(ThefapExtractor):
    """Extractor for individual items on thefap.com"""
    subcategory = "item"
    pattern = (BASE_PATTERN +
               r"/([^/?#]+)-(\d+)/([^/?#]+)/i(\d+)")
    example = "https://thefap.com/zoey.curly-374261/xpics/i1"

    def __init__(self, match):
        ThefapExtractor.__init__(self, match)
        self.root = text.root_from_url(match[0])
        self.model, self.model_id, self.kind, self.item_id = match.groups()

    def items(self):
        url = text.ensure_http_scheme(self.url)
        page = self.request(url).text
        if "Not Found" in page:
            raise exception.NotFoundError("item")

        data = {
            "model": self.model,
            "model_id": text.parse_int(self.model_id),
            "kind": self.kind,
            "item_id": text.parse_int(self.item_id),
        }
        yield Message.Directory, "", data

        seen = set()
        num = 0
        for media_url in self._extract_images(page, seen):
            num += 1
            data["num"] = num
            yield Message.Url, media_url, text.nameext_from_url(
                media_url, data)
