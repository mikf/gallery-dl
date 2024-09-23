# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://everia.club"""

from .common import Extractor, Message, exception
from .. import text
import itertools
import re


class EveriaExtractor(Extractor):
    category = "everia"
    subcategory = "post"
    root = "https://everia.club"
    pattern = r"(?:https?://)?everia\.club/(\d{4}/\d{2}/\d{2}/[^/]+)/?"
    example = "https://everia.club/YYYY/MM/DD/TITLE"
    directory_fmt = ("{category}", "{title}")

    def __init__(self, match):
        super().__init__(match)
        self.url = match.group(0)

    def extract(self, json):
        data = {
            "title": json["title"]["rendered"],
            "id": json["id"],
            "date": json["date"],
            "url": json["link"]
        }

        yield Message.Directory, data
        urls = re.findall(r'img.*?src=\"(.+?)\"', json["content"]["rendered"])
        for url in urls:
            yield Message.Url, url, text.nameext_from_url(url, data)

    def items(self):
        page = self.request(self.url).text
        json_url = text.extr(page, 'application/json" href="', '"')
        json = self.request(json_url).json()
        yield from self.extract(json)


class EveriaTagExtractor(EveriaExtractor):
    subcategory = "tag"
    pattern = r"(?:https?://)?everia\.club/tag/([^/]+)/?"
    example = "https://everia.club/tag/TAG"
    params = {"per_page": 34}

    def __init__(self, match):
        super().__init__(match)
        self.tag = match.group(1)

    def _pagination(self, pages=None):
        for self.params["page"] in itertools.count(1):
            url = "{}/wp-json/wp/v2/posts".format(self.root)
            try:
                response = self.request(url, params=self.params)
            except exception.HttpError:
                return
            for item in response.json():
                yield from self.extract(item)
            if self.params["page"] == pages:
                return

    def items(self):
        url = "{}/tag/{}".format(self.root, self.tag)
        page = self.request(url).text
        self.params["tags"] = text.extr(page, "wp/v2/tags/", '"')
        pages = text.rextract(page, "/page/", "/")[0] or 1
        yield from self._pagination(pages)


class EveriaSearchExtractor(EveriaTagExtractor):
    subcategory = "search"
    pattern = r"(?:https?://)?everia\.club/\?s=(.+)"
    example = "https://everia.club/?s=SEARCH"

    def __init__(self, match):
        super().__init__(match)
        self.params["search"] = match.group(1)

    def items(self):
        yield from self._pagination()
