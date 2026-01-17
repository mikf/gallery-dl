# -*- coding: utf-8 -*-

# Copyright 2024-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors forhttps://turbovid.cr/"""

# from .lolisafe import LolisafeAlbumExtractor
from gallery_dl.exception import HttpError
from gallery_dl.extractor.message import Message
from .. import text
from .common import Extractor

BASE_PATTERN = r"(?:https?://)?(?:turbo(?:vid)?\.cr)"



class TurboMediaExtractor(Extractor):
    """Extractor for turbo.cr videos"""
    category = "turbo"
    subcategory = "media"
    directory_fmt = ("{category}",)

    pattern = r"https?://(?:www\.)?turbo(?:vid)?\.cr(/(embe)?d/([^/?#]+))"
    example = "https://turbo.cr/embed/ID"

    def items(self):
        path, _, video_id = self.groups
        api_url = "https://turbo.cr/api/sign?v={}".format(video_id)

        try:
            response = self.request(api_url, headers={"Referer": self.root + path}).json()
        except HttpError as ex:
            self.log.error("%s: %s", ex.__class__.__name__, ex)
            return (), {}

        video_url = response.get("url")

        filename = response.get("filename")
        filename = response.get("filename").split(".")[0]

        if video_url:
            data = {
                "id"       : video_id,
                "filename" : filename,
                "extension": "mp4",
                "category" : self.category,
                "_http_headers": {
                    "Referer": self.root + path
                }
            }

            yield Message.Directory,"", data

            yield Message.Url, video_url, data

