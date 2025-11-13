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
    directory_fmt = ("{category}", "{user[full_name]} ({user[id]})",
                     "{channel[title]} ({channel[id]})")
    filename_fmt = "{num:>03}{block[id]:? //}.{extension}"
    archive_fmt = "{channel[id]}/{block[id]}"
    pattern = r"(?:https?://)?(?:www\.)?are\.na/[^/?#]+/([^/?#]+)"
    example = "https://are.na/evan-collins-1522646491/cassette-futurism"

    def metadata(self, page):
        channel = self.request_json(
            f"https://api.are.na/v2/channels/{self.groups[0]}")

        channel["date"] = self.parse_datetime_iso(
            channel["created_at"])
        channel["date_updated"] = self.parse_datetime_iso(
            channel["updated_at"])
        channel.pop("contents", None)

        return {
            "count"  : channel.get("length"),
            "user"   : channel.pop("user", None),
            "owner"  : channel.pop("owner", None),
            "channel": channel,
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

                block["date"] = self.parse_datetime_iso(
                    block["created_at"])
                block["date_updated"] = self.parse_datetime_iso(
                    block["updated_at"])

                yield url, {
                    "block" : block,
                    "source": block.pop("source", None),
                }

            if len(contents) < limit:
                return
            params["page"] += 1
