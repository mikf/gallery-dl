# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.vogue.com/photovogue/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vogue\.com/photovogue"


class PhotovogueUserExtractor(Extractor):
    category = "photovogue"
    subcategory = "user"
    directory_fmt = ("{category}", "{photographer[id]} {photographer[name]}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/photographers/(\d+)"
    example = "https://www.vogue.com/photovogue/photographers/12345"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = match.group(1)

    def items(self):
        for photo in self.photos():
            url = photo["gallery_image"]
            photo["title"] = photo["title"].strip()
            photo["date"] = text.parse_datetime(
                photo["date"], "%Y-%m-%dT%H:%M:%S.%f%z")

            yield Message.Directory, photo
            yield Message.Url, url, text.nameext_from_url(url, photo)

    def photos(self):
        url = "https://api.vogue.com/production/photos"
        params = {
            "count": "50",
            "order_by": "DESC",
            "page": 0,
            "photographer_id": self.user_id,
        }

        while True:
            data = self.request(url, params=params).json()
            yield from data["items"]

            if not data["has_next"]:
                break
            params["page"] += 1
