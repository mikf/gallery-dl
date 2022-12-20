# -*- coding: utf-8 -*-

# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://allthefallen.moe/"""

import re
from .common import GalleryExtractor
from .. import text

BASE_URL = "https://allthefallen.moe/forum/index.php?"


class AtfExtractor(GalleryExtractor):
    """Base class for ATF extractors"""
    category = "atf"
    root = "https://allthefallen.moe"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{subcategory}_{album_key}")
    archive_fmt = "{album_id}_{filename}"

    def __init__(self, match):
        url = BASE_URL + match.group(1) + "/"
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "album_id"   : self.gallery_url.rpartition(".")[2].strip("/"),
            "album_key"  : self.gallery_url.strip("/").rpartition("/")[2],
            "album_name" : text.unescape(extr('p-title-value">', "<")),
            "date"       : text.parse_datetime(extr('datetime="', '"')),
        }

    def _pagination(self):
        url = self.gallery_url
        page = 1
        while True:
            html = self.request(url).text
            yield html
            if "pageNav-jump--next" not in page:
                return
            page += 1
            url = self.gallery_url + "/page-" + page


class AtfThreadExtractor(AtfExtractor):
    """Extractor for ATF threads"""
    subcategory = "thread"
    pattern = (r"(?:https?://)?(?:www\.)?allthefallen\.moe/forum/index\.php\?"
               r"(threads/[^/?#]+)(/|/page-\d+)?")
    test = (
        (BASE_URL + "threads/i-take-requests.3583", {
            "keyword": {
                "album_id": "3583",
                "album_name": "I take requests...",
                "date": "dt:2016-06-10T08:14:52-0600",
            },
        }),
    )

    def images(self, _):
        for html in self._pagination():
            for href in re.findall(
                    r'href="/forum/index\.php\?attachments/(.+\.[0-9]+)/"',
                    html):
                url = BASE_URL + "attachments/" + href + "/"
                file = re.sub(r'-([0-9a-zA-Z]+)$', r'.\1',
                              href.rpartition(".")[0])
                file_parts = file.rpartition(".")
                yield url, {
                    "filename": file_parts[0],
                    "extension": file_parts[2],
                }


class AtfAlbumExtractor(AtfExtractor):
    """Extractor for ATF albums"""
    subcategory = "album"
    pattern = (r"(?:https?://)?(?:www\.)?allthefallen\.moe/forum/index\.php\?"
               r"(media/albums/[^/?#]+)(/|/page-\d+)?")
    test = (
        (BASE_URL + "media/albums/nishi-iori-random-np.970/", {
            "keyword": {
                "album_id": "970",
                "album_name": "Nishi Iori: RANDOM.NP",
                "date": "dt:2021-06-12T03:03:35-0600",
            },
        }),
    )

    def images(self, _):
        for html in self._pagination():
            for href in re.findall(
                    r'href="/forum/index\.php\?media/(.+\.[0-9]+)/"', html):
                if '/' in href:
                    continue
                url = BASE_URL + "media/" + href + "/full"
                file = re.sub(r'-([0-9a-zA-Z]+)$', r'.\1',
                              href.rpartition(".")[0])
                file_parts = file.rpartition(".")
                yield url, {
                    "filename": file_parts[0],
                    "extension": file_parts[2],
                }
