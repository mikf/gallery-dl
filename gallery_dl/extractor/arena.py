# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://are.na/"""

from .common import GalleryExtractor
from .. import text


class ArenaChannelExtractor(GalleryExtractor):
    """Extractor for are.na channels"""

    category = "arena"
    root = "https://are.na"
    pattern = r"(?:https?://)?(?:www\.)?are\.na(/[^/?#]+/[^/?#]+)"
    example = (
        "https://are.na/evan-collins-1522646491/cassette-futurism"
    )

    def __init__(self, match):
        GalleryExtractor.__init__(self, match)
        # Last path segment is the channel slug used by the API
        # self.page_url is guaranteed after GalleryExtractor init
        path = self.page_url.split("/", 3)[-1]
        self._channel_slug = path.rsplit("/", 1)[-1]

    def metadata(self, page):
        info = self.request_json(
            f"https://api.are.na/v2/channels/{self._channel_slug}")

        user = info.get("user") or {}
        data = {
            "gallery_id": info.get("slug") or str(info.get("id")),
            "channel_id": info.get("id"),
            "channel_slug": info.get("slug"),
            "title": info.get("title") or "",
            "count": info.get("length") or 0,
            "created_at": self.parse_datetime_iso(info.get("created_at")),
            "updated_at": self.parse_datetime_iso(info.get("updated_at")),
            "user_id": info.get("user_id"),
            "user_slug": user.get("slug") or "",
            "user_name": (user.get("full_name") or user.get("username")
                           or ""),
            "url": self.page_url,
        }
        return data

    def images(self, page):
        page_num = 1
        per = 100
        api = f"https://api.are.na/v2/channels/{self._channel_slug}/contents"

        while True:
            params = {"page": page_num, "per": per}
            data = self.request_json(api, params=params)

            contents = data.get("contents") or []
            if not contents:
                return

            for block in contents:
                url = None
                meta = {
                    "id": block.get("id"),
                    "block_class": block.get("class"),
                    "block_title": block.get("title") or block.get(
                        "generated_title") or "",
                }

                # Prefer original image
                image = block.get("image") or {}
                original = image.get("original") or {}
                if not url and original:
                    url = original.get("url")

                # Attachments (e.g., PDFs, files)
                if not url:
                    attach = block.get("attachment") or {}
                    url = attach.get("url")

                # Fallback to display/large image if present
                if not url and image:
                    disp = image.get("display") or {}
                    url = disp.get("url") or (image.get("large") or {}).get(
                        "url")

                # Some Links/Channels may not have downloadable media
                if not url:
                    continue

                # Provide source link if it exists
                src = block.get("source") or {}
                if src:
                    meta["source_url"] = src.get("url") or ""

                # Let gallery-dl infer filename/extension if not provided
                text.nameext_from_url(url, meta)

                yield url, meta
