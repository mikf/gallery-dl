# -*- coding: utf-8 -*-

# Copyright 2022 Ailothaen
# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Wikimedia and Wikipedia"""

from .common import BaseExtractor, Message
from .. import text


class WikimediaExtractor(BaseExtractor):
    """Base class for wikimedia extractors"""
    basecategory = "wikimedia"
    directory_fmt = ("{category}", "{page}")
    archive_fmt = "{sha1}"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.title = match.group(match.lastindex)

    def items(self):
        for info in self._pagination(self.params):
            image = info["imageinfo"][0]

            image["metadata"] = {
                m["name"]: m["value"]
                for m in image["metadata"]}
            image["commonmetadata"] = {
                m["name"]: m["value"]
                for m in image["commonmetadata"]}

            filename = image["canonicaltitle"]
            image["filename"], _, image["extension"] = \
                filename.partition(":")[2].rpartition(".")
            image["date"] = text.parse_datetime(
                image["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            image["page"] = self.title

            yield Message.Directory, image
            yield Message.Url, image["url"], image

    def _pagination(self, params):
        """
        https://www.mediawiki.org/wiki/API:Query
        https://opendata.stackexchange.com/questions/13381
        """

        url = self.root + "/w/api.php"
        params["action"] = "query"
        params["format"] = "json"

        while True:
            data = self.request(url, params=params).json()

            try:
                pages = data["query"]["pages"]
            except KeyError:
                pass
            else:
                yield from pages.values()

            try:
                continuation = data["continue"]
            except KeyError:
                break
            params.update(continuation)


BASE_PATTERN = WikimediaExtractor.update({
    "wikipedia": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikipedia\.org",
    },
    "wiktionary": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wiktionary\.org",
    },
    "wikiquote": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikiquote\.org",
    },
    "wikibooks": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikibooks\.org",
    },
    "wikisource": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikisource\.org",
    },
    "wikinews": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikinews\.org",
    },
    "wikiversity": {
        "root": None,
        "pattern": r"[a-z]{2,}\.wikiversity\.org",
    },
    "wikispecies": {
        "root": "https://species.wikimedia.org",
        "pattern": r"species\.wikimedia\.org",
    },
    "wikimediacommons": {
        "root": "https://commons.wikimedia.org",
        "pattern": r"commons\.wikimedia\.org",
    },
})


class WikimediaArticleExtractor(WikimediaExtractor):
    """Extractor for wikimedia articles"""
    subcategory = "article"
    pattern = BASE_PATTERN + r"/wiki/(?!Category:)([^/?#]+)"
    example = "https://en.wikipedia.org/wiki/TITLE"

    def _init(self):
        self.params = {
            "generator": "images",
            "titles"   : self.title,
            "prop"     : "imageinfo",
            "iiprop": "timestamp|user|userid|comment|canonicaltitle|url|size|"
                      "sha1|mime|metadata|commonmetadata|extmetadata|bitdepth",
        }


class WikimediaCategoryExtractor(WikimediaExtractor):
    subcategory = "category"
    pattern = BASE_PATTERN + r"/wiki/(Category:[^/?#]+)"
    example = "https://commons.wikimedia.org/wiki/Category:NAME"

    def _init(self):
        self.params = {
            "generator": "categorymembers",
            "gcmtitle" : self.title,
            "gcmtype"  : "file",
            "prop"     : "imageinfo",
            "iiprop": "timestamp|user|userid|comment|canonicaltitle|url|size|"
                      "sha1|mime|metadata|commonmetadata|extmetadata|bitdepth",
        }
