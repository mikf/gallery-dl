# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.plurk.com/"""

from .common import Extractor, Message
from .. import text, exception
import datetime
import json
import re


class PlurkExtractor(Extractor):
    """Base class for plurk extractors"""
    category = "plurk"
    root = "https://www.plurk.com"

    def items(self):
        yield Message.Version, 1
        for plurk in self.plurks():
            for url in text.extract_iter(plurk["content"], ' href="', '"'):
                yield Message.Queue, url, plurk

    def plurks(self):
        """Return an iterable with all relevant 'plurk' objects"""

    @staticmethod
    def _load(data):
        if not data:
            raise exception.NotFoundError("user")
        return json.loads(re.sub(r"new Date\(([^)]+)\)", r"\1", data))


class PlurkTimelineExtractor(PlurkExtractor):
    """Extractor for URLs from all posts in a Plurk timeline"""
    subcategory = "timeline"
    pattern = r"(?:https?://)?(?:www\.)?plurk\.com/(?!p/)(\w+)/?(?:$|[?&#])"
    test = ("https://www.plurk.com/plurkapi", {
        "pattern": r"https?://.+",
        "count": ">= 23"
    })

    def __init__(self, match):
        PlurkExtractor.__init__(self, match)
        self.user = match.group(1)

    def plurks(self):
        url = "{}/{}".format(self.root, self.user)
        page = self.request(url).text
        user_id, pos = text.extract(page, '"user_id":', ',')
        plurks = self._load(text.extract(page, "_PLURKS = ", ";\n", pos)[0])

        url = "https://www.plurk.com/TimeLine/getPlurks"
        headers = {
            "Referer": self.root + "/",
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {
            "user_id": user_id.strip(),
        }

        while plurks:
            yield from plurks

            offset = datetime.datetime.strptime(
                plurks[-1]["posted"], "%a, %d %b %Y %H:%M:%S %Z")
            data["offset"] = offset.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            response = self.request(
                url, method="POST", headers=headers, data=data)
            plurks = response.json()["plurks"]


class PlurkPostExtractor(PlurkExtractor):
    """Extractor for URLs from a Plurk post"""
    subcategory = "post"
    pattern = r"(?:https?://)?(?:www\.)?plurk\.com/p/(\w+)"
    test = ("https://www.plurk.com/p/i701j1", {
        "url": "2115f208564591b8748525c2807a84596aaaaa5f",
    })

    def __init__(self, match):
        PlurkExtractor.__init__(self, match)
        self.plurk_id = match.group(1)

    def plurks(self):
        url = "{}/p/{}".format(self.root, self.plurk_id)
        page = self.request(url).text
        user, pos = text.extract(page, " GLOBAL = ", "\n")
        data, pos = text.extract(page, "plurk = ", ";\n", pos)

        data = self._load(data)
        data["user"] = self._load(user)["page_user"]
        return (data,)
