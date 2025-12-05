# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pictoa.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:[\w]+\.)?pictoa\.com(?:\.de)?"


class PictoaExtractor(Extractor):
    """Base class for pictoa extractors"""
    category = "pictoa"
    root = "https://pictoa.com"
    directory_fmt = ("{category}", "{album_id} {album_title}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"


class PictoaImageExtractor(PictoaExtractor):
    """Extractor for single images from pictoa.com"""
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/albums/(?:[\w-]+-)?(\d+)/(\d+)"
    example = "https://www.pictoa.com/albums/NAME-12345/12345.html"

    def items(self):
        album_id, image_id = self.groups

        url = f"{self.root}/albums/{album_id}/{image_id}.html"
        page = self.request(url).text
        album_title = text.extr(page, 'property="og:title" content="', '"')
        image_url = text.extr(page, 'property="og:image" content="', '"')

        data = {
            "album_id"   : album_id,
            "album_title": album_title.rpartition(" #")[0],
            "id"         : image_id,
            "url"        : image_url,
        }

        text.nameext_from_url(image_url, data)
        yield Message.Directory, "", data
        yield Message.Url, image_url, data


class PictoaAlbumExtractor(PictoaExtractor):
    """Extractor for image albums from pictoa.com"""
    subcategory = "album"
    pattern = rf"{BASE_PATTERN}/albums/(?:[\w-]+-)?(\d+).html"
    example = "https://www.pictoa.com/albums/NAME-12345.html"

    def items(self):
        album_id = self.groups[0]
        url = f"{self.root}/albums/{album_id}.html"
        page = self.request(url).text

        album_data = {
            "album_id"   : album_id,
            "album_title": text.extr(page, "<h1>", "<"),
            "tags"       : text.split_html(text.extr(
                page, '<ol class="related-categories', '</ol>'))[1:],
            "_extractor" : PictoaImageExtractor,
        }

        while True:
            container = text.extr(page, '<main>', '<span id="flag" >')
            for url in text.extract_iter(
                    container, '<a rel="nofollow" href="', '"'):
                yield Message.Queue, url, album_data

            url = text.extr(page, '<link rel="next" href="', '"')
            if not url:
                break
            page = self.request(url).text
