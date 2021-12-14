# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.vogue.it/en/photovogue/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vogue\.it/(?:en/)?photovogue"


class PhotovogueUserExtractor(Extractor):
    category = "photovogue"
    subcategory = "user"
    directory_fmt = ("{category}", "{photographer[id]} {photographer[name]}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/portfolio/?\?id=(\d+)"
    test = (
        ("https://www.vogue.it/en/photovogue/portfolio/?id=221252"),
        ("https://vogue.it/photovogue/portfolio?id=221252", {
            "pattern": r"https://images.vogue.it/Photovogue/[^/]+_gallery.jpg",
            "keyword": {
                "date": "type:datetime",
                "favorite_count": int,
                "favorited": list,
                "id": int,
                "image_id": str,
                "is_favorite": False,
                "orientation": "re:portrait|landscape",
                "photographer": {
                    "biography": "Born in 1995. Live in Bologna.",
                    "city": "Bologna",
                    "country_id": 106,
                    "favoritedCount": int,
                    "id": 221252,
                    "isGold": bool,
                    "isPro": bool,
                    "latitude": str,
                    "longitude": str,
                    "name": "Arianna Mattarozzi",
                    "user_id": "38cb0601-4a85-453c-b7dc-7650a037f2ab",
                    "websites": list,
                },
                "photographer_id": 221252,
                "tags": list,
                "title": str,
            },
        }),
    )

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
        url = "https://api.vogue.it/production/photos"
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
