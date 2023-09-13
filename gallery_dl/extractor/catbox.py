# -*- coding: utf-8 -*-

# Copyright 2022-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://catbox.moe/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text


class CatboxAlbumExtractor(GalleryExtractor):
    """Extractor for catbox albums"""
    category = "catbox"
    subcategory = "album"
    root = "https://catbox.moe"
    filename_fmt = "{filename}.{extension}"
    directory_fmt = ("{category}", "{album_name} ({album_id})")
    archive_fmt = "{album_id}_{filename}"
    pattern = r"(?:https?://)?(?:www\.)?catbox\.moe(/c/[^/?#]+)"
    example = "https://catbox.moe/c/ID"

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "album_id"   : self.gallery_url.rpartition("/")[2],
            "album_name" : text.unescape(extr("<h1>", "<")),
            "date"       : text.parse_datetime(extr(
                "<p>Created ", "<"), "%B %d %Y"),
            "description": text.unescape(extr("<p>", "<")),
        }

    def images(self, page):
        return [
            ("https://files.catbox.moe/" + path, None)
            for path in text.extract_iter(
                page, ">https://files.catbox.moe/", "<")
        ]


class CatboxFileExtractor(Extractor):
    """Extractor for catbox files"""
    category = "catbox"
    subcategory = "file"
    archive_fmt = "{filename}"
    pattern = r"(?:https?://)?(?:files|litter|de)\.catbox\.moe/([^/?#]+)"
    example = "https://files.catbox.moe/NAME.EXT"

    def items(self):
        url = text.ensure_http_scheme(self.url)
        file = text.nameext_from_url(url, {"url": url})
        yield Message.Directory, file
        yield Message.Url, url, file
