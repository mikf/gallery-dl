# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://everia.club"""

from .common import Extractor, Message, exception
from .. import text
import functools
import itertools
import html
import re


class EveriaPostExtractor(Extractor):
    category = "everia"
    subcategory = "post"
    root = "https://everia.club/wp-json/wp/v2"
    pattern = r"(?:https?://)?everia\.club/(\d{4}/\d{2}/\d{2}/[^/]+)/?"
    example = "https://everia.club/YYYY/MM/DD/TITLE"
    directory_fmt = ("{category}", "{title}")

    def __init__(self, match):
        super().__init__(match)
        self.url = match.group(0)

    def get_tags(self, tag, type="tags"):
        if isinstance(tag, str):
            params = {"search": tag}
        elif isinstance(tag, int):
            params = {"include": tag}
        elif isinstance(tag, list):
            params = {"include": ",".join(map(str, tag))}

        url = "{}/{}".format(self.root, type)
        page = self.request(url, params=params).json()
        if isinstance(tag, str):
            return page[0]["id"]
        else:
            return [item["name"] for item in page]

    get_categories = functools.partialmethod(get_tags, type="categories")

    def extract(self, json):
        data = {
            "title": html.unescape(json["title"]["rendered"]),
            "id": json["id"],
            "date": json["date"],
            "url": text.unquote(json["link"]),
            "tags": self.get_tags(json["tags"]),
            "categories": self.get_categories(json["categories"]),
        }

        yield Message.Directory, data
        urls = re.findall(r'img.*?src=\"(.+?)\"', json["content"]["rendered"])
        for url in urls:
            text.nameext_from_url(text.unquote(url), data)
            yield Message.Url, url, data

    def items(self):
        page = self.request(self.url).text
        json_url = text.extr(page, 'application/json" href="', '"')
        json = self.request(json_url).json()
        yield from self.extract(json)


class EveriaTagExtractor(EveriaPostExtractor):
    subcategory = "tag"
    pattern = r"(?:https?://)?everia\.club/tag/([^/]+)/?"
    example = "https://everia.club/tag/TAG"
    params = {"per_page": 34}

    def __init__(self, match):
        super().__init__(match)
        self.tag = match.group(1)

    def _pagination(self, pages=None):
        for self.params["page"] in itertools.count(1):
            url = "{}/posts".format(self.root)
            try:
                json = self.request(url, params=self.params).json()
            except exception.HttpError:
                return
            for item in json:
                yield from self.extract(item)

    def items(self):
        self.params["tags"] = self.get_tags(self.tag)
        yield from self._pagination()


class EveriaSearchExtractor(EveriaTagExtractor):
    subcategory = "search"
    pattern = r"(?:https?://)?everia\.club/\?s=(.+)"
    example = "https://everia.club/?s=SEARCH"

    def __init__(self, match):
        super().__init__(match)
        self.params["search"] = match.group(1)

    def items(self):
        yield from self._pagination()


class EveriaCategoryExtractor(EveriaTagExtractor):
    subcategory = "category"
    pattern = r"(?:https?://)?everia\.club/category/([^/]+)/?"
    example = "https://everia.club/category/CATEGORY"

    def items(self):
        self.params["categories"] = self.get_categories(self.tag)
        yield from self._pagination()
