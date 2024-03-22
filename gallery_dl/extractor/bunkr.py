# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bunkr.sk/"""

from .lolisafe import LolisafeAlbumExtractor
from .. import text

BASE_PATTERN = (
    r"(?:https?://)?(?:app\.)?(bunkr+"
    r"\.(?:s[kiu]|ru|la|is|to|ac|black|cat|media|red|site|ws))"
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
    """Extractor for bunkr.sk albums"""
    category = "bunkr"
    root = "https://bunkr.sk"
    pattern = BASE_PATTERN + r"/a/([^/?#]+)"
    example = "https://bunkr.sk/a/ID"

    def __init__(self, match):
        LolisafeAlbumExtractor.__init__(self, match)
        domain = match.group(match.lastindex-1)
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
        return (
            text.extr(page, '<source src="', '"') or
            text.extr(page, '<img src="', '"') or
            text.rextract(page, ' href="', '"', page.rindex("Download"))[0]
        )


class BunkrMediaExtractor(BunkrAlbumExtractor):
    """Extractor for bunkr.sk media links"""
    subcategory = "media"
    directory_fmt = ("{category}",)
    pattern = BASE_PATTERN + r"(/[vid]/[^/?#]+)"
    example = "https://bunkr.sk/v/FILENAME"

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
        }
