# -*- coding: utf-8 -*-

# Copyright 2023-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Chevereto galleries"""

from .common import BaseExtractor, Message
from .. import text, util


class CheveretoExtractor(BaseExtractor):
    """Base class for chevereto extractors"""
    basecategory = "chevereto"
    directory_fmt = ("{category}", "{user}", "{album}")
    archive_fmt = "{id}"

    def _init(self):
        self.path = self.groups[-1]

    def _pagination(self, url):
        while True:
            page = self.request(url).text

            for item in text.extract_iter(
                    page, '<div class="list-item-image ', 'image-container'):
                yield text.urljoin(self.root, text.extr(
                    item, '<a href="', '"'))

            url = text.extr(page, 'data-pagination="next" href="', '"')
            if not url:
                return
            if url[0] == "/":
                url = self.root + url


BASE_PATTERN = CheveretoExtractor.update({
    "jpgfish": {
        "root": "https://jpg6.su",
        "pattern": r"(?:www\.)?jpe?g\d?\.(?:su|pet|fish(?:ing)?|church)",
    },
    "imagepond": {
        "root": "https://imagepond.net",
        "pattern": r"(?:www\.)?imagepond\.net",
    },
    "imglike": {
        "root": "https://imglike.com",
        "pattern": r"(?:www\.)?imglike\.com",
    },
})


class CheveretoImageExtractor(CheveretoExtractor):
    """Extractor for chevereto images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"(/im(?:g|age)/[^/?#]+)"
    example = "https://jpg2.su/img/TITLE.ID"

    def items(self):
        url = self.root + self.path
        page = self.request(url).text
        extr = text.extract_from(page)

        url = (extr('<meta property="og:image" content="', '"') or
               extr('url: "', '"'))
        if not url or url.endswith("/loading.svg"):
            pos = page.find(" download=")
            url = text.rextr(page, 'href="', '"', pos)
            if not url.startswith("https://"):
                url = util.decrypt_xor(
                    url, b"seltilovessimpcity@simpcityhatesscrapers",
                    fromhex=True)

        file = {
            "id"   : self.path.rpartition("/")[2].rpartition(".")[2],
            "url"  : url,
            "album": text.remove_html(extr(
                "Added to <a", "</a>").rpartition(">")[2]),
            "date" : text.parse_datetime(extr(
                '<span title="', '"'), "%Y-%m-%d %H:%M:%S"),
            "user" : extr('username: "', '"'),
        }

        text.nameext_from_url(file["url"], file)
        yield Message.Directory, file
        yield Message.Url, file["url"], file


class CheveretoVideoExtractor(CheveretoExtractor):
    """Extractor for chevereto videos"""
    subcategory = "video"
    pattern = BASE_PATTERN + r"(/video/[^/?#]+)"
    example = "https://imagepond.net/video/TITLE.ID"

    def items(self):
        url = self.root + self.path
        page = self.request(url).text
        extr = text.extract_from(page)

        file = {
            "id"       : self.path.rpartition(".")[2],
            "title"    : text.unescape(extr(
                'property="og:title" content="', '"')),
            "thumbnail": extr(
                'property="og:image" content="', '"'),
            "url"      : extr(
                'property="og:video" content="', '"'),
            "width"    : text.parse_int(extr(
                'property="video:width" content="', '"')),
            "height"   : text.parse_int(extr(
                'property="video:height" content="', '"')),
            "duration" : extr(
                'class="far fa-clock"></i>', "—"),
            "album": text.remove_html(extr(
                "Added to <a", "</a>").rpartition(">")[2]),
            "date"     : text.parse_datetime(extr(
                '<span title="', '"'), "%Y-%m-%d %H:%M:%S"),
            "user"     : extr('username: "', '"'),
        }

        try:
            min, _, sec = file["duration"].partition(":")
            file["duration"] = int(min) * 60 + int(sec)
        except Exception:
            pass

        text.nameext_from_url(file["url"], file)
        yield Message.Directory, file
        yield Message.Url, file["url"], file


class CheveretoAlbumExtractor(CheveretoExtractor):
    """Extractor for chevereto albums"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"(/a(?:lbum)?/[^/?#]+(?:/sub)?)"
    example = "https://jpg2.su/album/TITLE.ID"

    def items(self):
        url = self.root + self.path
        data_image = {"_extractor": CheveretoImageExtractor}
        data_video = {"_extractor": CheveretoVideoExtractor}

        if self.path.endswith("/sub"):
            albums = self._pagination(url)
        else:
            albums = (url,)

        for album in albums:
            for item_url in self._pagination(album):
                data = data_video if "/video/" in item_url else data_image
                yield Message.Queue, item_url, data


class CheveretoCategoryExtractor(CheveretoExtractor):
    """Extractor for chevereto galleries"""
    subcategory = "category"
    pattern = BASE_PATTERN + r"(/category/[^/?#]+)"
    example = "https://imglike.com/category/TITLE"

    def items(self):
        data = {"_extractor": CheveretoImageExtractor}
        for image in self._pagination(self.root + self.path):
            yield Message.Queue, image, data


class CheveretoUserExtractor(CheveretoExtractor):
    """Extractor for chevereto users"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(/[^/?#]+(?:/albums)?)"
    example = "https://jpg2.su/USER"

    def items(self):
        url = self.root + self.path

        if self.path.endswith("/albums"):
            data = {"_extractor": CheveretoAlbumExtractor}
            for url in self._pagination(url):
                yield Message.Queue, url, data
        else:
            data_image = {"_extractor": CheveretoImageExtractor}
            data_video = {"_extractor": CheveretoVideoExtractor}
            for url in self._pagination(url):
                data = data_video if "/video/" in url else data_image
                yield Message.Queue, url, data
