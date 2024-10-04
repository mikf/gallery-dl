# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.si/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text, config


if config.get(("extractor", "bunkr"), "tlds"):
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+\.\w+))"
    )
else:
    BASE_PATTERN = (
        r"(?:bunkr:(?:https?://)?([^/?#]+)|"
        r"(?:https?://)?(?:app\.)?(bunkr+"
        r"\.(?:s[kiu]|[cf]i|pk|ru|la|is|to|a[cx]"
        r"|black|cat|media|red|site|ws|org)))"
    )

LEGACY_DOMAINS = {
    "bunkr.ru",
    "bunkrr.ru",
    "bunkr.su",
    "bunkrr.su",
    "bunkr.la",
    "bunkr.is",
    "bunkr.to",
}


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

    def fetch_album(self, album_id):
        # album metadata
        page = self.request(self.root + "/a/" + self.album_id).text
        info = text.split_html(text.extr(
            page, "<h1", "</div>").partition(">")[2])
        count, _, size = info[1].split(None, 2)

        pos = page.index('class="grid-images')
        urls = list(text.extract_iter(page, '<a href="', '"', pos))

        return self._extract_files(urls), {
            "album_id"   : self.album_id,
            "album_name" : text.unescape(info[0]),
            "album_size" : size[1:-1],
            "count"      : len(urls),
            "_http_validate": self._validate,
        }

    def _extract_files(self, urls):
        for url in urls:
            try:
                url = self._extract_file(text.unescape(url))
            except Exception as exc:
                self.log.error("%s: %s", exc.__class__.__name__, exc)
                continue
            yield {"file": text.unescape(url)}

    def _extract_file(self, url):
        page = self.request(url).text
        url = (text.extr(page, '<source src="', '"') or
               text.extr(page, '<img src="', '"'))

        if not url:
            url_download = text.rextract(
                page, ' href="', '"', page.rindex("Download"))[0]
            page = self.request(text.unescape(url_download)).text
            url = text.unescape(text.rextract(page, ' href="', '"')[0])

        return url

    def _validate(self, response):
        if response.history and response.url.endswith("/maintenance-vid.mp4"):
            self.log.warning("File server in maintenance mode")
            return False
        return True


class BunkrMediaExtractor(BunkrAlbumExtractor):
    """Extractor for bunkr.si media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"(/[vid]/[^/?#]+)"
    example = "https://bunkr.si/v/FILENAME"

    def fetch_album(self, album_id):
        try:
            url = self._extract_file(self.root + self.album_id)
        except Exception as exc:
            self.log.error("%s: %s", exc.__class__.__name__, exc)
            return (), {}

        return ({"file": text.unescape(url)},), {
            "album_id"   : "",
            "album_name" : "",
            "album_size" : -1,
            "description": "",
            "count"      : 1,
            "_http_validate": self._validate,
        }
