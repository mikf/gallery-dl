# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://booth.pm/"""

from .common import Extractor, Message
from .. import text, util


class BoothExtractor(Extractor):
    """Base class for booth extractors"""
    category = "booth"
    root = "https://booth.pm"
    directory_fmt = ("{category}", "{shop[name]}", "{id} {name}")
    filename_fmt = "{num:>02} {filename}.{extension}"
    archive_fmt = "{id}_{filename}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.cookies.set("adult", "1", domain=".booth.pm")

    def items(self):
        for item in self.shop_items():
            item["_extractor"] = BoothItemExtractor
            yield Message.Queue, item["shop_item_url"], item

    def _pagination(self, url):
        while True:
            page = self.request(url).text

            for item in text.extract_iter(page, ' data-item="', '"'):
                yield util.json_loads(text.unescape(item))

            next = text.extr(page, 'rel="next" class="nav-item" href="', '"')
            if not next:
                break
            url = self.root + next


class BoothItemExtractor(BoothExtractor):
    subcategory = "item"
    pattern = r"(?:https?://)?(?:[\w-]+\.)?booth\.pm/(?:\w\w/)?items/(\d+)"
    example = "https://booth.pm/items/12345"

    def items(self):
        url = f"{self.root}/ja/items/{self.groups[0]}.json"
        item = self.request_json(url)

        item["booth_category"] = item.pop("category", None)
        item["date"] = text.parse_datetime(
            item["published_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        item["tags"] = [t["name"] for t in item["tags"]]

        files = self._extract_files(item)
        item["count"] = len(files)

        yield Message.Directory, item
        for num, file in enumerate(files, 1):
            url = file["url"]
            file["num"] = num
            text.nameext_from_url(url, file)
            yield Message.Url, url, {**item, **file}

    def _extract_files(self, item):
        files = []

        for image in item.pop("images"):
            url = image["original"].replace("_base_resized", "")
            files.append({
                "url"      : url,
                "_fallback": _fallback(url),
            })

        return files


class BoothShopExtractor(BoothExtractor):
    subcategory = "shop"
    pattern = r"(?:https?://)?([\w-]+\.)booth\.pm/(?:\w\w/)?(?:items)?"
    example = "https://SHOP.booth.pm/"

    def __init__(self, match):
        self.root = text.root_from_url(match[0])
        BoothExtractor.__init__(self, match)

    def shop_items(self):
        return self._pagination(f"{self.root}/items")


def _fallback(url):
    base = url[:-3]
    yield base + "jpeg"
    yield base + "png"
    yield base + "webp"
