# -*- coding: utf-8 -*-

# Copyright 2022 Ailothaen
# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Wikimedia sites"""

from .common import BaseExtractor, Message
from .. import text, exception
from ..cache import cache


class WikimediaExtractor(BaseExtractor):
    """Base class for wikimedia extractors"""
    basecategory = "wikimedia"
    filename_fmt = "{filename} ({sha1[:8]}).{extension}"
    archive_fmt = "{sha1}"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)

        if self.category == "wikimedia":
            self.category = self.root.split(".")[-2]
        elif self.category in ("fandom", "wikigg"):
            self.category = "{}-{}".format(
                self.category, self.root.partition(".")[0].rpartition("/")[2])

        self.per_page = self.config("limit", 50)

    def _init(self):
        api_path = self.config_instance("api-path")
        if api_path:
            if api_path[0] == "/":
                self.api_url = self.root + api_path
            else:
                self.api_url = api_path
        else:
            self.api_url = None

    @cache(maxage=36500*86400, keyarg=1)
    def _search_api_path(self, root):
        self.log.debug("Probing possible API endpoints")
        for path in ("/api.php", "/w/api.php", "/wiki/api.php"):
            url = root + path
            response = self.request(url, method="HEAD", fatal=None)
            if response.status_code < 400:
                return url
        raise exception.StopExtraction("Unable to find API endpoint")

    @staticmethod
    def prepare(image):
        """Adjust the content of an image object"""
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

    def items(self):
        for info in self._pagination(self.params):
            try:
                image = info["imageinfo"][0]
            except LookupError:
                self.log.debug("Missing 'imageinfo' for %s", info)
                continue

            self.prepare(image)
            yield Message.Directory, image
            yield Message.Url, image["url"], image

        if self.subcategories:
            base = self.root + "/wiki/"
            self.params["gcmtype"] = "subcat"
            for subcat in self._pagination(self.params):
                url = base + subcat["title"].replace(" ", "_")
                subcat["_extractor"] = WikimediaArticleExtractor
                yield Message.Queue, url, subcat

    def _pagination(self, params):
        """
        https://www.mediawiki.org/wiki/API:Query
        https://opendata.stackexchange.com/questions/13381
        """

        url = self.api_url
        if not url:
            url = self._search_api_path(self.root)

        params["action"] = "query"
        params["format"] = "json"
        params["prop"] = "imageinfo"
        params["iiprop"] = (
            "timestamp|user|userid|comment|canonicaltitle|url|size|"
            "sha1|mime|metadata|commonmetadata|extmetadata|bitdepth"
        )

        while True:
            data = self.request(url, params=params).json()

            # ref: https://www.mediawiki.org/wiki/API:Errors_and_warnings
            error = data.get("error")
            if error:
                self.log.error("%s: %s", error["code"], error["info"])
                return
            # MediaWiki will emit warnings for non-fatal mistakes such as
            # invalid parameter instead of raising an error
            warnings = data.get("warnings")
            if warnings:
                self.log.debug("MediaWiki returned warnings: %s", warnings)

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
        "api-path": "/api.php",
    },
    "wikigg": {
        "root": None,
        "pattern": r"\w+\.wiki\.gg",
        "api-path": "/api.php",
    },
    "mariowiki": {
        "root": "https://www.mariowiki.com",
        "pattern": r"(?:www\.)?mariowiki\.com",
        "api-path": "/api.php",
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
    directory_fmt = ("{category}", "{page}")
    pattern = BASE_PATTERN + r"/(?!static/)([^?#]+)"
    example = "https://en.wikipedia.org/wiki/TITLE"

    def __init__(self, match):
        WikimediaExtractor.__init__(self, match)

        path = self.groups[-1]
        if path[2] == "/":
            self.root = self.root + "/" + path[:2]
            path = path[3:]
        if path.startswith("wiki/"):
            path = path[5:]

        pre, sep, _ = path.partition(":")
        prefix = pre.lower() if sep else None

        self.title = path = text.unquote(path)
        if prefix:
            self.subcategory = prefix

        if prefix == "category":
            self.subcategories = \
                True if self.config("subcategories", True) else False
            self.params = {
                "generator": "categorymembers",
                "gcmtitle" : path,
                "gcmtype"  : "file",
                "gcmlimit" : self.per_page,
            }
        elif prefix == "file":
            self.subcategories = False
            self.params = {
                "titles"   : path,
            }
        else:
            self.subcategories = False
            self.params = {
                "generator": "images",
                "gimlimit" : self.per_page,
                "titles"   : path,
            }

    def prepare(self, image):
        WikimediaExtractor.prepare(image)
        image["page"] = self.title


class WikimediaWikiExtractor(WikimediaExtractor):
    """Extractor for all files on a MediaWiki instance"""
    subcategory = "wiki"
    pattern = BASE_PATTERN + r"/?$"
    example = "https://en.wikipedia.org/"

    def __init__(self, match):
        WikimediaExtractor.__init__(self, match)

        # ref: https://www.mediawiki.org/wiki/API:Allpages
        self.params = {
            "generator"   : "allpages",
            "gapnamespace": 6,  # "File" namespace
            "gaplimit"    : self.per_page,
        }
