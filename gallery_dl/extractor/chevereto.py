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
    parent = True

    def _init(self):
        self.path = self.groups[-1]

    def _pagination(self, url, callback=None):
        page = self.request(url).text
        if callback is not None:
            callback(page)

        while True:
            for item in text.extract_iter(
                    page, '<div class="list-item-image ', 'image-container'):
                yield text.urljoin(self.root, text.extr(
                    item, '<a href="', '"'))

            url = text.extr(page, 'data-pagination="next" href="', '"')
            if not url:
                return
            if url[0] == "/":
                url = self.root + url
            page = self.request(url).text


BASE_PATTERN = CheveretoExtractor.update({
    "jpgfish": {
        "root": "https://jpg7.cr",
        "pattern": r"(?:www\.)?jpe?g\d?\.(?:cr|su|pet|fish(?:ing)?|church)",
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
    pattern = rf"{BASE_PATTERN}(/im(?:g|age)/[^/?#]+)"
    example = "https://jpg7.cr/img/TITLE.ID"

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

        album_url, _, album_name = extr("Added to <a", "</a>").rpartition(">")
        file = {
            "id"   : self.path.rpartition("/")[2].rpartition(".")[2],
            "url"  : url,
            "album": text.remove_html(album_name),
            "date" : self.parse_datetime_iso(extr('<span title="', '"')),
            "user" : extr('username: "', '"'),
        }

        file["album_slug"], _, file["album_id"] = text.rextr(
            album_url, "/", '"').rpartition(".")

        text.nameext_from_url(file["url"], file)
        yield Message.Directory, "", file
        yield Message.Url, file["url"], file


class CheveretoVideoExtractor(CheveretoExtractor):
    """Extractor for chevereto videos"""
    subcategory = "video"
    pattern = rf"{BASE_PATTERN}(/video/[^/?#]+)"
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
            "album"    : extr(
                "Added to <a", "</a>"),
            "date"     : self.parse_datetime_iso(extr('<span title="', '"')),
            "user"     : extr('username: "', '"'),
        }

        album_url, _, album_name = file["album"].rpartition(">")
        file["album"] = text.remove_html(album_name)
        file["album_slug"], _, file["album_id"] = text.rextr(
            album_url, "/", '"').rpartition(".")

        try:
            min, _, sec = file["duration"].partition(":")
            file["duration"] = int(min) * 60 + int(sec)
        except Exception:
            pass

        text.nameext_from_url(file["url"], file)
        yield Message.Directory, "", file
        yield Message.Url, file["url"], file


class CheveretoAlbumExtractor(CheveretoExtractor):
    """Extractor for chevereto albums"""
    subcategory = "album"
    pattern = rf"{BASE_PATTERN}(/a(?:lbum)?/[^/?#]+(?:/sub)?)"
    example = "https://jpg7.cr/album/TITLE.ID"

    def items(self):
        url = self.root + self.path
        data_image = {"_extractor": CheveretoImageExtractor}
        data_video = {"_extractor": CheveretoVideoExtractor}

        if self.path.endswith("/sub"):
            albums = self._pagination(url)
        else:
            albums = (url,)

        kwdict = self.kwdict
        for album in albums:
            for kwdict["num"], item_url in enumerate(self._pagination(
                    album, self._extract_metadata_album), 1):
                data = data_video if "/video/" in item_url else data_image
                yield Message.Queue, item_url, data

    def _extract_metadata_album(self, page):
        url, pos = text.extract(
            page, 'property="og:url" content="', '"')
        title, pos = text.extract(
            page, 'property="og:title" content="', '"', pos)

        kwdict = self.kwdict
        kwdict["album_slug"], _, kwdict["album_id"] = \
            url[url.rfind("/")+1:].rpartition(".")
        kwdict["album"] = text.unescape(title)
        kwdict["count"] = text.parse_int(text.extract(
            page, 'data-text="image-count">', "<", pos)[0])


class CheveretoCategoryExtractor(CheveretoExtractor):
    """Extractor for chevereto galleries"""
    subcategory = "category"
    pattern = rf"{BASE_PATTERN}(/category/[^/?#]+)"
    example = "https://imglike.com/category/TITLE"

    def items(self):
        data = {"_extractor": CheveretoImageExtractor}
        for image in self._pagination(self.root + self.path):
            yield Message.Queue, image, data


class CheveretoUserExtractor(CheveretoExtractor):
    """Extractor for chevereto users"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}(/[^/?#]+(?:/albums)?)"
    example = "https://jpg7.cr/USER"

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
