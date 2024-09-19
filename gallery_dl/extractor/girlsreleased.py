# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://girlsreleased.com/"""

from .common import Extractor, Message

BASE_PATTERN = r"(?:https?://)?(?:www\.)?girlsreleased\.com"


class GirlsreleasedExtractor(Extractor):
    """Base class for girlsreleased extractors"""
    category = "girlsreleased"
    root = "https://www.girlsreleased.com/api/0.1"
    request_interval = 0.5
    request_interval_min = 0.2

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.id = match.group(1)

    def _images(self, json):
        data = {
            "title": json["name"] or json["id"],
            "id": json["id"],
            "site": json["site"],
            "model": ", ".join(model for _, model in json["models"])
        }
        yield Message.Directory, data
        for image in json["images"]:
            yield Message.Queue, image[3], data

    def _pagination(self, url):
        sets = []
        page = 0
        while True:
            json = self.request(url.format(self.root, self.id, page)).json()
            if not json["sets"]:
                return sets
            sets += json["sets"][1:]
            page += 1

    def items(self):
        sets = self.sets()

        if "images" in sets:
            yield from self._images(sets)
        else:
            for set in sets:
                url = "{}/set/{}".format(self.root, set[0])
                yield from self._images(self.request(url).json()["set"])


class GirlsreleasedSetExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased galleries"""
    subcategory = "set"
    pattern = BASE_PATTERN + r"/set/(\d+)"
    example = "https://girlsreleased.com/set/12345"

    def sets(self):
        url = "{}/set/{}".format(self.root, self.id)
        return self.request(url).json()["set"]


class GirlsreleasedModelExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased models"""
    subcategory = "model"
    pattern = BASE_PATTERN + r"/model/(\d+(?:/?.+)?)"
    example = "https://girlsreleased.com/model/12345/MODEL"

    def sets(self):
        return self._pagination("{}/sets/model/{}/page/{}")


class GirlsreleasedSiteExtractor(GirlsreleasedExtractor):
    """Extractor for girlsreleased sites"""
    subcategory = "site"
    pattern = BASE_PATTERN + r"/site/(.+(?:/model/\d+(?:/?.+)?)?)"
    example = "https://girlsreleased.com/site/SITE"

    def sets(self):
        return self._pagination("{}/sets/site/{}/page/{}")
