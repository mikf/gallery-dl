# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vk.com/"""

from .common import GalleryExtractor
from .. import text
import re


class VkAlbumExtractor(GalleryExtractor):
    """Extractor for vkontakte albums"""
    category = "vk"
    subcategory = "album"
    directory_fmt = ("{category}", "{album_id}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://vk.com/"
    pattern = r"(?:https://)?(?:www\.|m\.)?vk\.com/(?:albums|id)(\d+)"
    test = (
        ("https://vk.com/id398982326", {
            "pattern": r"https://sun\d+-\d+\.userapi\.com/c\d+/v\d+"
                       r"/[0-9a-f]+/[\w-]+\.jpg",
            "count": ">= 35",
        }),
        ("https://m.vk.com/albums398982326"),
        ("https://www.vk.com/id398982326"),
    )

    def __init__(self, match):
        self.album_id = match.group(1)
        url = "{}/albums{}".format(self.root, self.album_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        return {
            "album_id": self.album_id,
        }

    def images(self, page):
        results = []
        sub = re.compile(r"/imp[fg]/").sub
        needle = 'data-id="{}_'.format(self.album_id)

        for photo in text.extract_iter(page, needle, '?'):
            photo_id = photo.partition('"')[0]
            url = sub("/", photo.rpartition("(")[2])
            results.append((url, {"id": photo_id}))

        return results
