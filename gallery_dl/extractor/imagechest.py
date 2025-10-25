# -*- coding: utf-8 -*-

# Copyright 2020 Leonid "Bepis" Pavel
# Copyright 2023-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgchest.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text, util, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?imgchest\.com"


class ImagechestGalleryExtractor(GalleryExtractor):
    """Extractor for image galleries from imgchest.com"""
    category = "imagechest"
    root = "https://imgchest.com"
    pattern = rf"{BASE_PATTERN}/p/([A-Za-z0-9]{{11}})"
    example = "https://imgchest.com/p/abcdefghijk"

    def __init__(self, match):
        self.gallery_id = match[1]
        url = f"{self.root}/p/{self.gallery_id}"
        GalleryExtractor.__init__(self, match, url)

    def _init(self):
        if access_token := self.config("access-token"):
            self.api = self.utils().ImagechestAPI(self, access_token)
            self.page_url = None
            self.metadata = self._metadata_api

    def metadata(self, page):
        try:
            data = util.json_loads(text.unescape(text.extr(
                page, 'data-page="', '"')))
            post = data["props"]["post"]
        except Exception:
            if "<title>Not Found</title>" in page:
                raise exception.NotFoundError("gallery")
            self.files = ()
            return {}

        self.files = post.pop("files", ())
        post["gallery_id"] = self.gallery_id
        post["tags"] = [tag["name"] for tag in post["tags"]]

        return post

    def _metadata_api(self, page):
        post = self.api.post(self.gallery_id)

        post["date"] = self.parse_datetime_iso(post["created"])
        for img in post["images"]:
            img["date"] = self.parse_datetime_iso(img["created"])

        post["gallery_id"] = self.gallery_id
        post.pop("image_count", None)
        self.files = post.pop("images")

        return post

    def images(self, page):
        try:
            return [
                (file["link"], file)
                for file in self.files
            ]
        except Exception:
            return ()


class ImagechestUserExtractor(Extractor):
    """Extractor for imgchest.com user profiles"""
    category = "imagechest"
    subcategory = "user"
    root = "https://imgchest.com"
    pattern = rf"{BASE_PATTERN}/u/([^/?#]+)"
    example = "https://imgchest.com/u/USER"

    def items(self):
        for gallery in self.utils().posts(self, text.unquote(self.groups[0])):
            gallery["_extractor"] = ImagechestGalleryExtractor
            yield Message.Queue, gallery["link"], gallery
