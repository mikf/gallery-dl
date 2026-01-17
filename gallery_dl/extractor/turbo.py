# -*- coding: utf-8 -*-

# Copyright 2024-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors forhttps://turbovid.cr/"""

from gallery_dl.exception import HttpError
from gallery_dl.extractor.message import Message
from .common import Extractor

from .. import text

BASE_PATTERN = r"(?:https?://)?(?:turbo(?:vid)?\.cr)"

class TurboAlbumMediaExtractor(Extractor):
    """Extractor for turbo.cr album files"""
    category = "turbo"
    subcategory = "media"
    directory_fmt = ("{category}",)

    pattern = r"https?://(?:www\.)?turbo(?:vid)?\.cr(/a/([^/?#]+))"
    example = "https://turbo.cr/a/ID"

    def items(self):
        path, _ = self.groups

        try:
            # FIXME: self.root is empty by default
            response = self.request(
                self.url,
            )

            tbody, _ = text.extract(response.text, '<tbody id="fileTbody"', '</tbody>')
            if not tbody:
                raise Exception("Could not extract files from site")

            ids = list(text.extract_iter(tbody, 'data-id="', '"'))

            if not ids:
                raise Exception("Could not extract files from site")

        except Exception as ex:
            self.log.error("%s: %s", ex.__class__.__name__, ex)
            return (), {}

        files = []
        api_url = "https://turbo.cr/api/sign?v={}"

        for v_id in ids:
            try:
                response = self.request(
                    api_url.format(v_id),
                ).json()
            except HttpError as ex:
                self.log.error("%s: %s", ex.__class__.__name__, ex)
                return (), {}

            video_url = response.get("url")

            filename = response.get("filename")
            filename = response.get("filename").split(".")[0]

            files.append(
                {
                    "id"       : v_id,
                    "url"       : video_url,
                    "filename" : filename,
                    "extension": "mp4",
                    "category" : self.category,
                    "_http_headers": {
                        "Referer": self.root + path
                    }
                }
            )

        for data in files:
            yield Message.Directory, "", data
            yield Message.Url, data["url"], data


class TurboMediaExtractor(Extractor):
    """Extractor for turbo.cr single files"""
    category = "turbo"
    subcategory = "media"
    directory_fmt = ("{category}",)

    pattern = r"https?://(?:www\.)?turbo(?:vid)?\.cr(/(embe)?(v)?d/([^/?#]+))"
    example = "https://turbo.cr/embed/ID"

    def items(self):
        path, _, video_id = self.groups
        api_url = "https://turbo.cr/api/sign?v={}".format(video_id)

        try:
            response = self.request(
                api_url,
            ).json()
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

            yield Message.Directory, "", data

            yield Message.Url, video_url, data
