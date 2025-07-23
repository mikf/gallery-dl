# -*- coding: utf-8 -*-

# Copyright 2021-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://picarto.tv/"""

from .common import Extractor, Message
from .. import text


class PicartoGalleryExtractor(Extractor):
    """Extractor for picarto galleries"""
    category = "picarto"
    subcategory = "gallery"
    root = "https://picarto.tv"
    directory_fmt = ("{category}", "{channel[name]}")
    filename_fmt = "{id} {title}.{extension}"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?picarto\.tv/([^/?#]+)/gallery"
    example = "https://picarto.tv/USER/gallery/TITLE/"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.username = match[1]

    def items(self):
        for post in self.posts():
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%d %H:%M:%S")
            variations = post.pop("variations", ())
            yield Message.Directory, post

            image = post["default_image"]
            if not image:
                continue
            url = "https://images.picarto.tv/gallery/" + image["name"]
            text.nameext_from_url(url, post)
            yield Message.Url, url, post

            for variation in variations:
                post.update(variation)
                image = post["default_image"]
                url = "https://images.picarto.tv/gallery/" + image["name"]
                text.nameext_from_url(url, post)
                yield Message.Url, url, post

    def posts(self):
        url = "https://ptvintern.picarto.tv/api/channel-gallery"
        params = {
            "first": "30",
            "page": 1,
            "filter_params[album_id]": "",
            "filter_params[channel_name]": self.username,
            "filter_params[q]": "",
            "filter_params[visibility]": "",
            "order_by[field]": "published_at",
            "order_by[order]": "DESC",
        }

        while True:
            posts = self.request_json(url, params=params)
            if not posts:
                return
            yield from posts
            params["page"] += 1
