# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://yourlesbians.com/"""

from .common import GalleryExtractor
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?yourlesbians\.com"


class YourlesbiansAlbumExtractor(GalleryExtractor):
    category = "yourlesbians"
    subcategory = "album"
    root = "https://yourlesbians.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{num:>03} {filename}.{extension}"
    archive_fmt = "{title}/{num}"
    pattern = BASE_PATTERN + r"(/album/([^/?#]+)/?)"
    example = "https://yourlesbians.com/album/SLUG/"

    def metadata(self, page):
        extr = text.extract_from(page)
        data = {
            "album_url": extr('property="og:url" content="', '"'),
            "title": text.unescape(extr(
                'property="og:title" content="', '"')[:-8].rstrip()),
            "album_thumbnail": extr('property="og:image" content="', '"'),
            "description": extr('property="og:description" content="', '"'),
            "tags": text.split_html(extr('tags-row', '</div>'))[1:],
        }
        if data["description"].endswith(", right after."):
            data["description"] = ""
        self.album = extr('class="album-inner', "</div>")
        return data

    def images(self, _):
        results = []
        for url in text.extract_iter(self.album, '<a href="', '"'):
            fn, _, ext = url.rsplit("/", 2)[1].rpartition(".")
            results.append((url, {
                "filename" : fn,
                "extension": ext,
            }))
        return results
