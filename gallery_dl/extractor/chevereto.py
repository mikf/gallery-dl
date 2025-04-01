# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
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
    directory_fmt = ("{category}", "{user}", "{album}",)
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
        "root": "https://jpg5.su",
        "pattern": r"jpe?g\d?\.(?:su|pet|fish(?:ing)?|church)",
    },
    "imgkiwi": {
        "root": "https://img.kiwi",
        "pattern": r"img\.kiwi",
    },
    "imagepond": {
        "root": "https://imagepond.net",
        "pattern": r"imagepond\.net",
    },
})


class CheveretoImageExtractor(CheveretoExtractor):
    """Extractor for chevereto Images"""
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
            url = text.rextract(page, 'href="', '"', pos)[0]
            if not url.startswith("https://"):
                url = util.decrypt_xor(
                    url, b"seltilovessimpcity@simpcityhatesscrapers",
                    fromhex=True)

        image = {
            "id"   : self.path.rpartition(".")[2],
            "url"  : url,
            "album": text.extr(extr("Added to <a", "/a>"), ">", "<"),
            "user" : extr('username: "', '"'),
        }

        text.nameext_from_url(image["url"], image)
        yield Message.Directory, image
        yield Message.Url, image["url"], image


class CheveretoAlbumExtractor(CheveretoExtractor):
    """Extractor for chevereto Albums"""
    subcategory = "album"
    pattern = BASE_PATTERN + r"(/a(?:lbum)?/[^/?#]+(?:/sub)?)"
    example = "https://jpg2.su/album/TITLE.ID"

    def items(self):
        url = self.root + self.path
        data = {"_extractor": CheveretoImageExtractor}

        if self.path.endswith("/sub"):
            albums = self._pagination(url)
        else:
            albums = (url,)

        for album in albums:
            for image in self._pagination(album):
                yield Message.Queue, image, data


class CheveretoUserExtractor(CheveretoExtractor):
    """Extractor for chevereto Users"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(/(?!img|image|a(?:lbum)?)[^/?#]+(?:/albums)?)"
    example = "https://jpg2.su/USER"

    def items(self):
        url = self.root + self.path

        if self.path.endswith("/albums"):
            data = {"_extractor": CheveretoAlbumExtractor}
        else:
            data = {"_extractor": CheveretoImageExtractor}

        for url in self._pagination(url):
            yield Message.Queue, url, data
