# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://lexica.art/"""

from .common import Extractor, Message
from .. import text


class LexicaSearchExtractor(Extractor):
    """Extractor for lexica.art search results"""
    category = "lexica"
    subcategory = "search"
    root = "https://lexica.art"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?lexica\.art/?\?q=([^&#]+)"
    test = (
        ("https://lexica.art/?q=tree", {
            "pattern": r"https://lexica-serve-encoded-images2\.sharif\."
                       r"workers.dev/full_jpg/[0-9a-f-]{36}$",
            "range": "1-80",
            "count": 80,
            "keyword": {
                "height": int,
                "id": str,
                "upscaled_height": int,
                "upscaled_width": int,
                "userid": str,
                "width": int,
                "prompt": {
                    "c": int,
                    "grid": bool,
                    "height": int,
                    "id": str,
                    "images": list,
                    "initImage": None,
                    "initImageStrength": None,
                    "model": "lexica-aperture-v2",
                    "negativePrompt": str,
                    "prompt": str,
                    "seed": str,
                    "timestamp": r"re:\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\dZ",
                    "width": int,
                },
            },
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.group(1)
        self.text = text.unquote(self.query).replace("+", " ")

    def items(self):
        base = ("https://lexica-serve-encoded-images2.sharif.workers.dev"
                "/full_jpg/")
        tags = self.text

        for image in self.posts():
            image["filename"] = image["id"]
            image["extension"] = "jpg"
            image["search_tags"] = tags
            yield Message.Directory, image
            yield Message.Url, base + image["id"], image

    def posts(self):
        url = self.root + "/api/infinite-prompts"
        headers = {
            "Accept" : "application/json, text/plain, */*",
            "Referer": "{}/?q={}".format(self.root, self.query),
        }
        json = {
            "text"      : self.text,
            "searchMode": "images",
            "source"    : "search",
            "cursor"    : 0,
            "model"     : "lexica-aperture-v2",
        }

        while True:
            data = self.request(
                url, method="POST", headers=headers, json=json).json()

            prompts = {
                prompt["id"]: prompt
                for prompt in data["prompts"]
            }

            for image in data["images"]:
                image["prompt"] = prompts[image["promptid"]]
                del image["promptid"]
                yield image

            cursor = data.get("nextCursor")
            if not cursor:
                return

            json["cursor"] = cursor
