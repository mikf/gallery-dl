# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.vogue.it/en/photovogue/"""

from .common import Extractor, Message
from datetime import datetime

BASE_PATTERN = r"(?:https?://)?(?:www.vogue.it(?:/en)?/photovogue)"


class PhotovogueUserExtractor(Extractor):
    category = "photovogue"
    subcategory = "user"
    directory_fmt = ("{category}", "{photographer[id]}_{photographer[name]}")
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.vogue.it/en/photovogue/"
    pattern = BASE_PATTERN + r"/portfolio/\?id=(\d+)"
    test = (
        ("https://www.vogue.it/en/photovogue/portfolio/?id=221252",),
        ("https://www.vogue.it/photovogue/portfolio/?id=221252",),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = match.group(1)

    def _photos(self):
        page = 0

        while True:
            res = self.request(
                "https://api.vogue.it/production/photos",
                params={
                    "count": 50,
                    "order_by": "DESC",
                    "page": page,
                    "photographer_id": self.user_id,
                },
            ).json()

            for item in res["items"]:
                item["extension"] = "jpg"
                item["title"] = item["title"].strip()
                item["_mtime"] = datetime.fromisoformat(
                    item["date"].replace("Z", "+00:00")
                ).timestamp()

                yield item

            if not res["has_next"]:
                break

            page += 1

    def items(self):
        yield Message.Version, 1

        yielded_dir = False

        for photo in self._photos():
            if not yielded_dir:
                yield Message.Directory, photo
                yielded_dir = True

            yield Message.Url, photo["gallery_image"], photo
