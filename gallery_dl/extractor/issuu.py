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

        data = text.extr(
            page, '{\\"documentTextVersion\\":', ']\\n"])</script>')
        data = util.json_loads(text.unescape(
            '{"":' + data.replace('\\"', '"')))

        doc = data["initialDocumentData"]["document"]
        doc["date"] = text.parse_datetime(
            doc["originalPublishDateInISOString"], "%Y-%m-%dT%H:%M:%S.%fZ")

        self._cnt = text.parse_int(doc["pageCount"])
        self._tpl = "https://{}/{}-{}/jpg/page_{{}}.jpg".format(
            "image.isu.pub",  # data["config"]["hosts"]["image"],
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
    pattern = r"(?:https?://)?issuu\.com/([^/?#]+)(?:/(\d*))?$"
    example = "https://issuu.com/USER"

    def items(self):
        user, pnum = self.groups
        base = self.root + "/" + user
        pnum = text.parse_int(pnum, 1)

        while True:
            url = base + "/" + str(pnum) if pnum > 1 else base
            try:
                html = self.request(url).text
                data = text.extr(html, '\\"docs\\":', '}]\\n"]')
                docs = util.json_loads(data.replace('\\"', '"'))
            except Exception as exc:
                self.log.debug("", exc_info=exc)
                return

            for publication in docs:
                url = self.root + "/" + publication["uri"]
                publication["_extractor"] = IssuuPublicationExtractor
                yield Message.Queue, url, publication

            if len(docs) < 48:
                return
            pnum += 1
