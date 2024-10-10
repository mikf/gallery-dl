# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Chevereto galleries"""

from .common import BaseExtractor, Message
from .. import text


class CheveretoExtractor(BaseExtractor):
    """Base class for chevereto extractors"""
    basecategory = "chevereto"
    directory_fmt = ("{category}", "{user}", "{album}",)
    archive_fmt = "{id}"

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.path = match.group(match.lastindex)

    def _pagination(self, url):
        while url:
            page = self.request(url).text

            for item in text.extract_iter(
                    page, '<div class="list-item-image ', 'image-container'):
                yield text.extr(item, '<a href="', '"')

            url = text.extr(page, '<a data-pagination="next" href="', '" ><')


BASE_PATTERN = CheveretoExtractor.update({
    "jpgfish": {
        "root": "https://jpg5.su",
        "pattern": r"jpe?g\d?\.(?:su|pet|fish(?:ing)?|church)",
    },
    "imgkiwi": {
        "root": "https://img.kiwi",
        "pattern": r"img\.kiwi",
    },
})


class CheveretoImageExtractor(CheveretoExtractor):
    """Extractor for chevereto Images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"(/im(?:g|age)/[^/?#]+)"
    example = "https://jpg2.su/img/TITLE.ID"

    def items(self):
        url = self.root + self.path
        extr = text.extract_from(self.request(url).text)

        image = {
            "id"   : self.path.rpartition(".")[2],
            "url"  : extr('<meta property="og:image" content="', '"'),
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
