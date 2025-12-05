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
        self.cookies.set("adult", "t", domain=".booth.pm")

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
        url = f"{self.root}/ja/items/{self.groups[0]}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRF-Token": None,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
        }

        if self.config("strategy") == "fallback":
            page = None
            item = self.request_json(url + ".json", headers=headers)
        else:
            page = self.request(url).text
            headers["X-CSRF-Token"] = text.extr(
                page, 'name="csrf-token" content="', '"')
            item = self.request_json(
                url + ".json", headers=headers, interval=False)

        item["booth_category"] = item.pop("category", None)
        item["date"] = self.parse_datetime_iso(item["published_at"])
        item["tags"] = [t["name"] for t in item["tags"]]

        shop = item["shop"]
        shop["id"] = text.parse_int(shop["thumbnail_url"].rsplit("/", 3)[1])

        if files := self._extract_files(item, page):
            item["count"] = len(files)
            shop["uuid"] = files[0]["url"].split("/", 4)[3]
        else:
            item["count"] = 0
            shop["uuid"] = util.NONE

        yield Message.Directory, "", item
        for num, file in enumerate(files, 1):
            url = file["url"]
            file["num"] = num
            text.nameext_from_url(url, file)
            yield Message.Url, url, {**item, **file}

    def _extract_files(self, item, page):
        if page is None:
            files = []
            for image in item.pop("images"):
                url = image["original"].replace("_base_resized", "")
                files.append({
                    "url"      : url,
                    "_fallback": _fallback(url),
                })
            return files

        del item["images"]
        return [{"url": url}
                for url in text.extract_iter(page, 'data-origin="', '"')]


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
