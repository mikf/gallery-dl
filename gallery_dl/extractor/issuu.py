# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://issuu.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util
import json


class IssuuBase():
    """Base class for issuu extractors"""
    category = "issuu"
    root = "https://issuu.com"


class IssuuPublicationExtractor(IssuuBase, GalleryExtractor):
    """Extractor for a single publication"""
    subcategory = "publication"
    directory_fmt = ("{category}", "{document[userName]}",
                     "{document[originalPublishDate]} {document[title]}")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{document[id]}_{num}"
    pattern = r"(?:https?://)?issuu\.com(/[^/?#]+/docs/[^/?#]+)"
    test = ("https://issuu.com/issuu/docs/motions-1-2019/", {
        "pattern": r"https://image.isu.pub/190916155301-\w+/jpg/page_\d+.jpg",
        "count"  : 36,
        "keyword": {
            "document": {
                "access"        : "public",
                "articleStories": list,
                "contentRating" : dict,
                "date"          : "dt:2019-09-16 00:00:00",
                "description"   : "re:Motions, the brand new publication by I",
                "documentId"    : r"re:\d+-d99ec95935f15091b040cb8060f05510",
                "documentName"  : "motions-1-2019",
                "downloadState" : "NOT_AVAILABLE",
                "id"            : r"re:\d+-d99ec95935f15091b040cb8060f05510",
                "isConverting"  : False,
                "isQuarantined" : False,
                "lang"          : "en",
                "language"      : "English",
                "pageCount"     : 36,
                "publicationId" : "d99ec95935f15091b040cb8060f05510",
                "title"         : "Motions by Issuu - Issue 1",
                "userName"      : "issuu",
            },
            "extension": "jpg",
            "filename" : r"re:page_\d+",
            "num"      : int,
        },
    })

    def metadata(self, page):
        data = json.loads(text.extract(
            page, 'window.__INITIAL_STATE__ =', ';\n')[0])

        doc = data["document"]
        doc["lang"] = doc["language"]
        doc["language"] = util.code_to_language(doc["language"])
        doc["date"] = text.parse_datetime(
            doc["originalPublishDate"], "%Y-%m-%d")

        self._cnt = text.parse_int(doc["pageCount"])
        self._tpl = "https://{}/{}/jpg/page_{{}}.jpg".format(
            data["config"]["hosts"]["image"], doc["id"])

        return {"document": doc}

    def images(self, page):
        fmt = self._tpl.format
        return [(fmt(i), None) for i in range(1, self._cnt + 1)]


class IssuuUserExtractor(IssuuBase, Extractor):
    """Extractor for all publications of a user/publisher"""
    subcategory = "user"
    pattern = r"(?:https?://)?issuu\.com/([^/?#]+)/?$"
    test = ("https://issuu.com/issuu", {
        "pattern": IssuuPublicationExtractor.pattern,
        "count"  : "> 25",
    })

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
