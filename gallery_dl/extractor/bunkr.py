# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.si/"""

from .common import Extractor
from .lolisafe import LolisafeAlbumExtractor
from .. import text, config, exception
import random

if config.get(("extractor", "bunkr"), "tlds"):
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+\.\w+))"
    )
else:
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+"
        r"\.(?:s[kiu]|[cf]i|p[hks]|ru|la|is|to|a[cx]"
        r"|black|cat|media|red|site|ws|org)))"
    )

DOMAINS = [
    "bunkr.ac",
    "bunkr.ci",
    "bunkr.fi",
    "bunkr.ph",
    "bunkr.pk",
    "bunkr.ps",
    "bunkr.si",
    "bunkr.sk",
    "bunkr.ws",
    "bunkr.black",
    "bunkr.red",
    "bunkr.media",
    "bunkr.site",
]
LEGACY_DOMAINS = {
    "bunkr.ax",
    "bunkr.cat",
    "bunkr.ru",
    "bunkrr.ru",
    "bunkr.su",
    "bunkrr.su",
    "bunkr.la",
    "bunkr.is",
    "bunkr.to",
}
CF_DOMAINS = set()


class BunkrAlbumExtractor(LolisafeAlbumExtractor):
    """Extractor for bunkr.si albums"""
    category = "bunkr"
    root = "https://bunkr.si"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://bunkr.si/a/ID"

    def __init__(self, match):
        LolisafeAlbumExtractor.__init__(self, match)
        domain = self.groups[0] or self.groups[1]
        if domain not in LEGACY_DOMAINS:
            self.root = "https://" + domain

    def request(self, url, **kwargs):
        kwargs["allow_redirects"] = False

        while True:
            try:
                response = Extractor.request(self, url, **kwargs)
                if response.status_code < 300:
                    return response

                # redirect
                url = response.headers["Location"]
                root, path = self._split(url)
                if root not in CF_DOMAINS:
                    continue
                self.log.debug("Redirect to known CF challenge domain '%s'",
                               root)

            except exception.HttpError as exc:
                if exc.status != 403:
                    raise

                # CF challenge
                root, path = self._split(url)
                CF_DOMAINS.add(root)
                self.log.debug("Added '%s' to CF challenge domains", root)

                try:
                    DOMAINS.remove(root.rpartition("/")[2])
                except ValueError:
                    pass
                else:
                    if not DOMAINS:
                        raise exception.StopExtraction(
                            "All Bunkr domains require solving a CF challenge")

            # select alternative domain
            root = "https://" + random.choice(DOMAINS)
            self.log.debug("Trying '%s' as fallback", root)
            url = root + path

    def fetch_album(self, album_id):
        # album metadata
        page = self.request(self.root + "/a/" + self.album_id).text
        title, size = text.split_html(text.extr(
            page, "<h1", "</span>").partition(">")[2])

        items = list(text.extract_iter(page, "<!-- item -->", "<!--  -->"))
        return self._extract_files(items), {
            "album_id"   : self.album_id,
            "album_name" : title,
            "album_size" : text.extr(size, "(", ")"),
            "count"      : len(items),
        }

    def _extract_files(self, items):
        for item in items:
            try:
                url = text.extr(item, ' href="', '"')
                file = self._extract_file(text.unescape(url))

                info = text.split_html(item)
                file["name"] = info[0]
                file["size"] = info[2]
                file["date"] = text.parse_datetime(
                    info[-1], "%H:%M:%S %d/%m/%Y")

                yield file
            except exception.StopExtraction:
                raise
            except Exception as exc:
                self.log.error("%s: %s", exc.__class__.__name__, exc)
                self.log.debug("", exc_info=exc)

    def _extract_file(self, webpage_url):
        response = self.request(webpage_url)
        page = response.text
        file_url = (text.extr(page, '<source src="', '"') or
                    text.extr(page, '<img src="', '"'))

        if not file_url:
            webpage_url = text.unescape(text.rextract(
                page, ' href="', '"', page.rindex("Download"))[0])
            response = self.request(webpage_url)
            file_url = text.rextract(response.text, ' href="', '"')[0]

        return {
            "file"          : text.unescape(file_url),
            "_http_headers" : {"Referer": response.url},
            "_http_validate": self._validate,
        }

    def _validate(self, response):
        if response.history and response.url.endswith("/maintenance-vid.mp4"):
            self.log.warning("File server in maintenance mode")
            return False
        return True

    def _split(self, url):
        pos = url.index("/", 8)
        return url[:pos], url[pos:]


class BunkrMediaExtractor(BunkrAlbumExtractor):
    """Extractor for bunkr.si media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"(/[vid]/[^/?#]+)"
    example = "https://bunkr.si/v/FILENAME"

    def fetch_album(self, album_id):
        try:
            file = self._extract_file(self.root + album_id)
        except Exception as exc:
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            return (), {}

        return (file,), {
            "album_id"   : "",
            "album_name" : "",
            "album_size" : -1,
            "description": "",
            "count"      : 1,
        }
