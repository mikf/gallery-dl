# -*- coding: utf-8 -*-

# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://piczel.tv/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?piczel\.tv"


class PiczelExtractor(Extractor):
    """Base class for piczel extractors"""
    category = "piczel"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{category}_{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    root = "https://piczel.tv"
    root_api = root

    def items(self):
        for post in self.posts():
            post["tags"] = [t["title"] for t in post["tags"] if t["title"]]
            post["date"] = self.parse_datetime_iso(post["created_at"])

            if post["multi"]:
                images = post["images"]
                del post["images"]
                post["count"] = len(images)
                yield Message.Directory, "", post
                for post["num"], image in enumerate(images):
                    if "id" in image:
                        del image["id"]
                    post.update(image)
                    url = post["image"]["url"]
                    yield Message.Url, url, text.nameext_from_url(url, post)

            else:
                post["count"] = 1
                yield Message.Directory, "", post
                post["num"] = 0
                url = post["image"]["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        """Return an iterable with all relevant post objects"""

    def _pagination(self, url, pnum=1):
        params = {"page": pnum}

        while True:
            data = self.request_json(url, params=params)

            yield from data["data"]

            params["page"] = data["meta"]["next_page"]
            if not params["page"]:
                return


class PiczelUserExtractor(PiczelExtractor):
    """Extractor for all images from a user's gallery"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/gallery/([^/?#]+)/?$"
    example = "https://piczel.tv/gallery/USER"

    def posts(self):
        url = f"{self.root_api}/api/users/{self.groups[0]}/gallery"
        return self._pagination(url)


class PiczelFolderExtractor(PiczelExtractor):
    """Extractor for images inside a user's folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user[username]}", "{folder[name]}")
    archive_fmt = "f{folder[id]}_{id}_{num}"
    pattern = rf"{BASE_PATTERN}/gallery/(?!image/)[^/?#]+/(\d+)"
    example = "https://piczel.tv/gallery/USER/12345"

    def posts(self):
        url = f"{self.root_api}/api/gallery/folder/{self.groups[0]}"
        return self._pagination(url)


class PiczelImageExtractor(PiczelExtractor):
    """Extractor for individual images"""
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/gallery/image/(\d+)"
    example = "https://piczel.tv/gallery/image/12345"

    def posts(self):
        url = f"{self.root_api}/api/gallery/{self.groups[0]}"
        return (self.request_json(url),)
