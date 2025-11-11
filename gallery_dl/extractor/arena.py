# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for https://are.na/"""

from .common import GalleryExtractor


class ArenaChannelExtractor(GalleryExtractor):
    """Extractor for are.na channels"""
    category = "arena"
    subcategory = "channel"
    root = "https://are.na"
    pattern = r"(?:https?://)?(?:www\.)?are\.na/[^/?#]+/([^/?#]+)"
    example = "https://are.na/evan-collins-1522646491/cassette-futurism"

    def metadata(self, page):
        info = self.request_json(
            f"https://api.are.na/v2/channels/{self.groups[0]}")

        return {
            "gallery_id"  : info.get("slug") or str(info.get("id")),
            "channel_id"  : info.get("id"),
            "channel_slug": info.get("slug"),
            "title"       : info.get("title") or "",
            "count"       : info.get("length") or 0,
            "user"        : info.get("user"),
            "date"        : self.parse_datetime_iso(info.get("created_at")),
            "date_updated": self.parse_datetime_iso(info.get("updated_at")),
        }

    def images(self, page):
        api = f"https://api.are.na/v2/channels/{self.groups[0]}/contents"
        limit = 100
        params = {"page": 1, "per": limit}

        while True:
            data = self.request_json(api, params=params)

            contents = data.get("contents")
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

                # Attachments (e.g., PDFs, files)
                if attachment := block.get("attachment"):
                    url = attachment.get("url")

                # Images
                elif image := block.get("image"):
                    # Prefer original image
                    if original := image.get("original"):
                        url = original.get("url")
                    # Fallback to display/large image if present
                    elif display := image.get("display"):
                        url = display.get("url")
                    elif large := image.get("large"):
                        url = large.get("url")

                # Some Links/Channels may not have downloadable media
                if not url:
                    continue

                # Provide source link if it exists
                if src := block.get("source"):
                    meta["source_url"] = src.get("url") or ""

                yield url, meta

            if len(contents) < limit:
                return
            params["page"] += 1
