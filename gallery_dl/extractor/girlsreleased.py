# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://girlsreleased.com/"""

from .common import Extractor, Message
from .. import text
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?girlsreleased\.com"


class GirlsreleasedExtractor(Extractor):
    """Base class for girlsreleased extractors"""
    category = "girlsreleased"
    root = "https://girlsreleased.com"
    request_interval = 0.5
    request_interval_min = 0.2

    def items(self):
        data = {"_extractor": GirlsreleasedSetExtractor}
        base = f"{self.root}/set/"
        for set in self._pagination():
            yield Message.Queue, f"{base}{set[0]}", data

    def _pagination(self):
        base = f"{self.root}/api/0.2/sets/{self._path}/{self.groups[0]}/page/"
        for pnum in itertools.count():
            sets = self.request_json(f"{base}{pnum}")["sets"]
            if not sets:
                return

            yield from sets[1:] if pnum else sets
            if len(sets) < 80:
                return


class GirlsreleasedSetExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased galleries"""
    subcategory = "set"
    pattern = rf"{BASE_PATTERN}/set/(\d+)"
    example = "https://girlsreleased.com/set/12345"

    def items(self):
        url = f"{self.root}/api/0.2/set/{self.groups[0]}"
        json = self.request_json(url)["set"]
        data = {
            "title": json["name"] or json["id"],
            "id": json["id"],
            "site": json["site"],
            "model": [model for _, model in json["models"]],
            "date": self.parse_timestamp(json["date"]),
            "count": len(json["images"]),
            "url": "https://girlsreleased.com/set/" + json["id"],
        }
        yield Message.Directory, "", data
        for data["num"], image in enumerate(json["images"], 1):
            text.nameext_from_url(image[5], data)
            yield Message.Queue, image[3], data


class GirlsreleasedModelExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased models"""
    subcategory = _path = "model"
    pattern = rf"{BASE_PATTERN}/model/(\d+(?:/.+)?)"
    example = "https://girlsreleased.com/model/12345/MODEL"


class GirlsreleasedSiteExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased sites"""
    subcategory = _path = "site"
    pattern = rf"{BASE_PATTERN}/site/([^/?#]+(?:/model/\d+/?.*)?)"
    example = "https://girlsreleased.com/site/SITE"
