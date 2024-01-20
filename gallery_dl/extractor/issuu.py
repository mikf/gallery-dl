# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://issuu.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util


class IssuuBase():
    """Base class for issuu extractors"""
    category = "issuu"
    root = "https://issuu.com"


class IssuuPublicationExtractor(IssuuBase, GalleryExtractor):
    """Extractor for a single publication"""
    subcategory = "publication"
    directory_fmt = ("{category}", "{document[username]}",
                     "{document[date]:%Y-%m-%d} {document[title]}")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{document[publicationId]}_{num}"
    pattern = r"(?:https?://)?issuu\.com(/[^/?#]+/docs/[^/?#]+)"
    example = "https://issuu.com/issuu/docs/TITLE/"

    def metadata(self, page):
        pos = page.rindex('id="initial-data"')
        data = util.json_loads(text.rextract(
            page, '<script data-json="', '"', pos)[0].replace("&quot;", '"'))

        doc = data["initialDocumentData"]["document"]
        doc["date"] = text.parse_datetime(
            doc["originalPublishDateInISOString"], "%Y-%m-%dT%H:%M:%S.%fZ")

        self._cnt = text.parse_int(doc["pageCount"])
        self._tpl = "https://{}/{}-{}/jpg/page_{{}}.jpg".format(
            data["config"]["hosts"]["image"],
            doc["revisionId"],
            doc["publicationId"],
        )

        return {"document": doc}

    def images(self, page):
        fmt = self._tpl.format
        return [(fmt(i), None) for i in range(1, self._cnt + 1)]


class IssuuUserExtractor(IssuuBase, Extractor):
    """Extractor for all publications of a user/publisher"""
    subcategory = "user"
    pattern = r"(?:https?://)?issuu\.com/([^/?#]+)/?$"
    example = "https://issuu.com/USER"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def items(self):
        url = "{}/call/profile/v1/documents/{}".format(self.root, self.user)
        params = {"offset": 0, "limit": "25"}

        while True:
            data = self.request(url, params=params).json()

            for publication in data["items"]:
                publication["url"] = "{}/{}/docs/{}".format(
                    self.root, self.user, publication["uri"])
                publication["_extractor"] = IssuuPublicationExtractor
                yield Message.Queue, publication["url"], publication

            if not data["hasMore"]:
                return
            params["offset"] += data["limit"]
