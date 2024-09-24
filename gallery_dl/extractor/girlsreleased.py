# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://girlsreleased.com/"""

from .common import Extractor, Message
from .. import text
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?girlsreleased\.com"


class GirlsreleasedSetExtractor(Extractor):
    """Extractor for girlsreleased galleries"""
    category = "girlsreleased"
    subcategory = "set"
    pattern = BASE_PATTERN + r"/set/(\d+)"
    example = "https://girlsreleased.com/set/12345"
    root = "https://www.girlsreleased.com/api/0.1"
    request_interval = 0.5
    request_interval_min = 0.2

    def __init__(self, match):
        super().__init__(match)
        self.id = match.group(1)

    def images(self, id):
        url = "{}/set/{}".format(self.root, id)
        json = self.request(url).json()["set"]
        data = {
            "title": json["name"] or json["id"],
            "id": json["id"],
            "site": json["site"],
            "model": [model for _, model in json["models"]]
        }
        yield Message.Directory, data
        for image in json["images"]:
            text.nameext_from_url(image[5], data)
            yield Message.Queue, image[3], data

    def items(self):
        yield from self.images(self.id)


class GirlsreleasedModelExtractor(GirlsreleasedSetExtractor):
    """Extractor for girlsreleased models"""
    subcategory = "model"
    pattern = BASE_PATTERN + r"/model/(\d+(?:/?.+)?)"
    example = "https://girlsreleased.com/model/12345/MODEL"

    def _pagination(self):
        for page in itertools.count():
            url = "{}/sets/{}/{}/page/{}".format(
                self.root, self.subcategory, self.id, page
            )
            json = self.request(url).json()["sets"]
            if not json:
                return
            offset = 0 if page == 0 else 1
            yield from json[offset:]

    def items(self):
        for set in self._pagination():
            yield from self.images(set[0])


class GirlsreleasedSiteExtractor(GirlsreleasedModelExtractor):
    """Extractor for girlsreleased sites"""
    subcategory = "site"
    pattern = BASE_PATTERN + r"/site/(.+(?:/model/\d+(?:/?.+)?)?)"
    example = "https://girlsreleased.com/site/SITE"
