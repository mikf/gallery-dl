# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://https://pixeldrain.com/"""

from .common import GalleryExtractor
from .. import text, util


class PixeldrainGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from pixeldrain.com"""
    category = "pixeldrain"
    root = "https://pixeldrain.com"
    pattern = r"(?:https?://)?(?:www\.)?pixeldrain\.com(/l/[^/?#]+)"
    example = "https://pixeldrain.com/l/12345xyz"

    def metadata(self, page):
        data = util.json_loads(text.extr(
            page, "window.viewer_data = ", ";"))["api_response"]
        data["gallery_id"] = data["id"]
        data["date"] = text.parse_datetime(
            data["date_created"], "%Y-%m-%dT%H:%M:%S.%f%z")
        self._files = data.pop("files", ())
        return data

    def images(self, _):
        ufmt = "{}/api/file/{}".format
        return [
            (ufmt(self.root, file["id"]), text.nameext_from_url(file["name"], {
                "upload_date": text.parse_datetime(
                    file["date_upload"], "%Y-%m-%dT%H:%M:%S.%f%z"),
                "file": file,
            }))
            for file in self._files
        ]
