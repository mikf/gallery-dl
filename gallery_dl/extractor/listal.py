# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://listal.com"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?listal\.com"


class ListalExtractor(Extractor):
    """Base class for Listal extractor"""
    category = "listal"
    root = "https://www.listal.com"
    directory_fmt = ("{category}", "{title}")
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{id}/{filename}"

    def items(self):
        for image_id in self.image_ids():
            img = self._extract_image(image_id)
            url = img["url"]
            text.nameext_from_url(url, img)
            yield Message.Directory, "", img
            yield Message.Url, url, img

    def _pagination(self, base_url, pnum=None):
        if pnum is None:
            url = base_url
            pnum = 1
        else:
            url = f"{base_url}/{pnum}"

        while True:
            page = self.request(url).text

            yield page

            if pnum is None or "<span class='nextprev'>Next" in page:
                return
            pnum += 1
            url = f"{base_url}/{pnum}"

    def _extract_image(self, image_id):
        url = f"{self.root}/viewimage/{image_id}h"
        page = self.request(url).text
        extr = text.extract_from(page)

        return {
            "id"        : image_id,
            "url"       : extr("<div><center><img src='", "'"),
            "title"     : text.unescape(extr('title="', '"')),
            "width"     : text.parse_int(extr("width='", "'")),
            "height"    : text.parse_int(extr("height='", "'")),
            "author_url": extr("Added by <a href='", "'"),
            "author"    : text.unescape(extr(">", "<")),
            "date"      : self.parse_datetime(extr(
                " ago on ", "<"), "%d %B %Y %H:%M"),
        }


class ListalImageExtractor(ListalExtractor):
    """Extractor for listal pictures"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/viewimage/(\d+)"
    example = "https://www.listal.com/viewimage/12345678"

    def image_ids(self):
        return (self.groups[0],)


class ListalPeopleExtractor(ListalExtractor):
    """Extractor for listal people pictures"""
    subcategory = "people"
    pattern = BASE_PATTERN + r"/([^/?#]+)/pictures"
    example = "https://www.listal.com/NAME/pictures"

    def image_ids(self):
        url = f"{self.root}/{self.groups[0]}/pictures"
        for page in self._pagination(url):
            yield from text.extract_iter(page, "listal.com/viewimage/", "'")
