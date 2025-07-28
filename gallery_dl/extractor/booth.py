# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://booth.pm/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:[\w-]+\.)?booth\.pm(?:/\w\w)?"


class BoothExtractor(Extractor):
    """Base class for booth extractors"""
    category = "booth"
    root = "https://booth.pm"
    directory_fmt = ("{category}", "{shop[name]}", "{id} {name}")
    filename_fmt = "{num:>02} {filename}.{extension}"
    archive_fmt = "{id}_{filename}"

    def _init(self):
        self.cookies.set("adult", "1", domain=".booth.pm")


class BoothItemExtractor(BoothExtractor):
    subcategory = "item"
    pattern = BASE_PATTERN + r"/items/(\d+)"
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


def _fallback(url):
    base = url[:-3]
    yield base + "jpeg"
    yield base + "png"
    yield base + "webp"
