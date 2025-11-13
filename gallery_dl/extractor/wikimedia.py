# -*- coding: utf-8 -*-

# Copyright 2022 Ailothaen
# Copyright 2024-2025 Mike Fährmann
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
        self._init_category(match)

        self.format = False
        if self.category == "wikimedia":
            labels = self.root.split(".")
            self.lang = labels[-3][-2:]
            self.category = labels[-2]
        elif self.category in ("fandom", "wikigg"):
            self.lang = "en"
            self.format = "original"
            self.basesubcategory = self.category
            self.category = (
                f"{self.category}-"
                f"{self.root.partition('.')[0].rpartition('/')[2]}")
        else:
            self.lang = ""

        if useragent := self.config_instance("useragent"):
            self.useragent = useragent

        BaseExtractor.__init__(self, match)

    def _init(self):
        if api_path := self.config_instance("api-path"):
            if api_path[0] == "/":
                self.api_url = f"{self.root}{api_path}"
            else:
                self.api_url = api_path
        else:
            self.api_url = None

        # note: image revisions are different from page revisions
        # ref:
        # https://www.mediawiki.org/wiki/API:Revisions
        # https://www.mediawiki.org/wiki/API:Imageinfo
        self.image_revisions = self.config("image-revisions", 1)
        self.format = self.config("format", self.format)
        self.per_page = self.config("limit", 50)
        self.subcategories = False

    @cache(maxage=36500*86400, keyarg=1)
    def _search_api_path(self, root):
        self.log.debug("Probing possible API endpoints")
        for path in ("/api.php", "/w/api.php", "/wiki/api.php"):
            url = f"{root}{path}"
            response = self.request(url, method="HEAD", fatal=None)
            if response.status_code < 400:
                return url
        raise exception.AbortExtraction("Unable to find API endpoint")

    def prepare_info(self, info):
        """Adjust the content of an image info object"""

    def prepare_image(self, image):
        """Adjust the content of an image object"""
        image["metadata"] = {
            m["name"]: m["value"]
            for m in image["metadata"] or ()}
        image["commonmetadata"] = {
            m["name"]: m["value"]
            for m in image["commonmetadata"] or ()}

        text.nameext_from_name(
            image["canonicaltitle"].partition(":")[2], image)
        image["date"] = self.parse_datetime_iso(image["timestamp"])

        if self.format:
            url = image["url"]
            image["url"] = (f"{url}{'&' if '?' in url else '?'}"
                            f"format={self.format}")

    def items(self):
        params = self.params()

        for info in self._pagination(params):
            try:
                images = info.pop("imageinfo")
            except KeyError:
                self.log.debug("Missing 'imageinfo' for %s", info)
                images = ()

            info["count"] = len(images)
            self.prepare_info(info)
            yield Message.Directory, info

            num = 0
            for image in images:
                # https://www.mediawiki.org/wiki/Release_notes/1.34
                if "filemissing" in image:
                    self.log.warning(
                        "File %s (or its revision) is missing",
                        image["canonicaltitle"].partition(":")[2])
                    continue
                num += 1
                image["num"] = num
                self.prepare_image(image)
                image.update(info)
                yield Message.Url, image["url"], image

        if self.subcategories:
            base = f"{self.root}/wiki/"
            params["gcmtype"] = "subcat"
            for subcat in self._pagination(params):
                url = f"{base}{subcat['title'].replace(' ', '_')}"
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
        params["iilimit"] = self.image_revisions

        while True:
            data = self.request_json(url, params=params)

            # ref: https://www.mediawiki.org/wiki/API:Errors_and_warnings
            if error := data.get("error"):
                self.log.error("%s: %s", error["code"], error["info"])
                return
            # MediaWiki will emit warnings for non-fatal mistakes such as
            # invalid parameter instead of raising an error
            if warnings := data.get("warnings"):
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
        "useragent": "Googlebot-Image/1.0",
    },
})


class WikimediaArticleExtractor(WikimediaExtractor):
    """Extractor for wikimedia articles"""
    subcategory = "article"
    directory_fmt = ("{category}", "{page}")
    pattern = rf"{BASE_PATTERN}/(?!static/)([^?#]+)"
    example = "https://en.wikipedia.org/wiki/TITLE"

    def __init__(self, match):
        WikimediaExtractor.__init__(self, match)

        path = self.groups[-1]
        if path[2] == "/":
            self.lang = lang = path[:2]
            self.root = f"{self.root}/{lang}"
            path = path[3:]
        if path.startswith("wiki/"):
            path = path[5:]
        self.path = text.unquote(path)

        pre, sep, _ = path.partition(":")
        self.prefix = prefix = pre.lower() if sep else None
        if prefix is not None:
            self.subcategory = prefix

    def params(self):
        if self.prefix == "category":
            if self.config("subcategories", True):
                self.subcategories = True
            return {
                "generator": "categorymembers",
                "gcmtitle" : self.path,
                "gcmtype"  : "file",
                "gcmlimit" : self.per_page,
            }

        if self.prefix == "file":
            return {
                "titles": self.path,
            }

        return {
            "generator": "images",
            "gimlimit" : self.per_page,
            "titles"   : self.path,
        }

    def prepare_info(self, info):
        info["page"] = self.path
        info["lang"] = self.lang


class WikimediaWikiExtractor(WikimediaExtractor):
    """Extractor for all files on a MediaWiki instance"""
    subcategory = "wiki"
    pattern = rf"{BASE_PATTERN}/?$"
    example = "https://en.wikipedia.org/"

    def params(self):
        # ref: https://www.mediawiki.org/wiki/API:Allpages
        return {
            "generator"   : "allpages",
            "gapnamespace": 6,  # "File" namespace
            "gaplimit"    : self.per_page,
        }
