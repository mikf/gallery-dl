# -*- coding: utf-8 -*-

# Copyright 2022 Ailothaen
# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Wikimedia sites"""

from .common import BaseExtractor, Message
from .. import text


class WikimediaExtractor(BaseExtractor):
    """Base class for wikimedia extractors"""
    basecategory = "wikimedia"
    filename_fmt = "{filename} ({sha1[:8]}).{extension}"
    directory_fmt = ("{category}", "{page}")
    archive_fmt = "{sha1}"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        path = match.group(match.lastindex)

        if self.category == "wikimedia":
            self.category = self.root.split(".")[-2]
        elif self.category in ("fandom", "wikigg"):
            self.category = "{}-{}".format(
                self.category, self.root.partition(".")[0].rpartition("/")[2])

        if path.startswith("wiki/"):
            path = path[5:]

        pre, sep, _ = path.partition(":")
        prefix = pre.lower() if sep else None

        self.title = path = text.unquote(path)
        if prefix:
            self.subcategory = prefix

        if prefix == "category":
            self.params = {
                "generator": "categorymembers",
                "gcmtitle" : path,
                "gcmtype"  : "file",
            }
        elif prefix == "file":
            self.params = {
                "titles"   : path,
            }
        else:
            self.params = {
                "generator": "images",
                "titles"   : path,
            }

    def _init(self):
        api_path = self.config_instance("api-path")
        if api_path:
            if api_path[0] == "/":
                self.api_url = self.root + api_path
            else:
                self.api_url = api_path
        else:
            self.api_url = self.root + "/api.php"

    def items(self):
        for info in self._pagination(self.params):
            try:
                image = info["imageinfo"][0]
            except LookupError:
                self.log.debug("Missing 'imageinfo' for %s", info)
                continue

            image["metadata"] = {
                m["name"]: m["value"]
                for m in image["metadata"] or ()}
            image["commonmetadata"] = {
                m["name"]: m["value"]
                for m in image["commonmetadata"] or ()}

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

        url = self.api_url
        params["action"] = "query"
        params["format"] = "json"
        params["prop"] = "imageinfo"
        params["iiprop"] = (
            "timestamp|user|userid|comment|canonicaltitle|url|size|"
            "sha1|mime|metadata|commonmetadata|extmetadata|bitdepth"
        )

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
    "wikimedia": {
        "root": None,
        "pattern": r"[a-z]{2,}\."
                   r"wik(?:i(?:pedia|quote|books|source|news|versity|data"
                   r"|voyage)|tionary)"
                   r"\.org",
        "api-path": "/w/api.php",
    },
    "wikispecies": {
        "root": "https://species.wikimedia.org",
        "pattern": r"species\.wikimedia\.org",
        "api-path": "/w/api.php",
    },
    "wikimediacommons": {
        "root": "https://commons.wikimedia.org",
        "pattern": r"commons\.wikimedia\.org",
        "api-path": "/w/api.php",
    },
    "mediawiki": {
        "root": "https://www.mediawiki.org",
        "pattern": r"(?:www\.)?mediawiki\.org",
        "api-path": "/w/api.php",
    },
    "fandom": {
        "root": None,
        "pattern": r"[\w-]+\.fandom\.com",
    },
    "wikigg": {
        "root": None,
        "pattern": r"\w+\.wiki\.gg",
    },
    "mariowiki": {
        "root": "https://www.mariowiki.com",
        "pattern": r"(?:www\.)?mariowiki\.com",
    },
    "bulbapedia": {
        "root": "https://bulbapedia.bulbagarden.net",
        "pattern": r"(?:bulbapedia|archives)\.bulbagarden\.net",
        "api-path": "/w/api.php",
    },
    "pidgiwiki": {
        "root": "https://www.pidgi.net",
        "pattern": r"(?:www\.)?pidgi\.net",
        "api-path": "/wiki/api.php",
    },
    "azurlanewiki": {
        "root": "https://azurlane.koumakan.jp",
        "pattern": r"azurlane\.koumakan\.jp",
        "api-path": "/w/api.php",
    },
})


class WikimediaArticleExtractor(WikimediaExtractor):
    """Extractor for wikimedia articles"""
    subcategory = "article"
    pattern = BASE_PATTERN + r"/(?!static/)([^?#]+)"
    example = "https://en.wikipedia.org/wiki/TITLE"
