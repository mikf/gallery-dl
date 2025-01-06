# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.plurk.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import datetime
import re


class PlurkExtractor(Extractor):
    """Base class for plurk extractors"""
    category = "plurk"
    root = "https://www.plurk.com"
    request_interval = (0.5, 1.5)

    def items(self):
        urls = self._urls_ex if self.config("comments", False) else self._urls
        for plurk in self.plurks():
            for url in urls(plurk):
                yield Message.Queue, url, plurk

    def plurks(self):
        """Return an iterable with all relevant 'plurk' objects"""

    @staticmethod
    def _urls(obj):
        """Extract URLs from a 'plurk' object"""
        return text.extract_iter(obj["content"], ' href="', '"')

    def _urls_ex(self, plurk):
        """Extract URLs from a 'plurk' and its comments"""
        yield from self._urls(plurk)
        for comment in self._comments(plurk):
            yield from self._urls(comment)

    def _comments(self, plurk):
        """Return an iterable with a 'plurk's comments"""
        url = "https://www.plurk.com/Responses/get"
        data = {"plurk_id": plurk["id"], "count": "200"}
        headers = {
            "Origin": self.root,
            "Referer": self.root,
            "X-Requested-With": "XMLHttpRequest",
        }

        while True:
            info = self.request(
                url, method="POST", headers=headers, data=data).json()
            yield from info["responses"]
            if not info["has_newer"]:
                return
            elif info["has_newer"] < 200:
                del data["count"]
            data["from_response_id"] = info["responses"][-1]["id"] + 1

    @staticmethod
    def _load(data):
        if not data:
            raise exception.NotFoundError("user")
        return util.json_loads(re.sub(r"new Date\(([^)]+)\)", r"\1", data))


class PlurkTimelineExtractor(PlurkExtractor):
    """Extractor for URLs from all posts in a Plurk timeline"""
    subcategory = "timeline"
    pattern = r"(?:https?://)?(?:www\.)?plurk\.com/(?!p/)(\w+)/?(?:$|[?#])"
    example = "https://www.plurk.com/USER"

    def __init__(self, match):
        PlurkExtractor.__init__(self, match)
        self.user = match.group(1)

    def plurks(self):
        url = "{}/{}".format(self.root, self.user)
        page = self.request(url).text
        user_id, pos = text.extract(page, '"page_user": {"id":', ',')
        plurks = self._load(text.extract(page, "_PLURKS = ", ";\n", pos)[0])

        headers = {"Referer": url, "X-Requested-With": "XMLHttpRequest"}
        data = {"user_id": user_id.strip()}
        url = "https://www.plurk.com/TimeLine/getPlurks"

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
    example = "https://www.plurk.com/p/12345"

    def plurks(self):
        url = "{}/p/{}".format(self.root, self.groups[0])
        page = self.request(url).text
        user, pos = text.extract(page, " GLOBAL=", "\n")
        data, pos = text.extract(page, "plurk =", ";\n", pos)

        data = self._load(data)
        try:
            data["user"] = self._load(user)["page_user"]
        except Exception:
            self.log.warning("%s: Failed to extract 'user' data",
                             self.groups[0])
        return (data,)
