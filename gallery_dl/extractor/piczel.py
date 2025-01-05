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
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            if post["multi"]:
                images = post["images"]
                del post["images"]
                post["count"] = len(images)
                yield Message.Directory, post
                for post["num"], image in enumerate(images):
                    if "id" in image:
                        del image["id"]
                    post.update(image)
                    url = post["image"]["url"]
                    yield Message.Url, url, text.nameext_from_url(url, post)

            else:
                post["count"] = 1
                yield Message.Directory, post
                post["num"] = 0
                url = post["image"]["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        """Return an iterable with all relevant post objects"""

    def _pagination(self, url, pnum=1):
        params = {"page": pnum}

        while True:
            data = self.request(url, params=params).json()

            yield from data["data"]

            params["page"] = data["meta"]["next_page"]
            if not params["page"]:
                return


class PiczelUserExtractor(PiczelExtractor):
    """Extractor for all images from a user's gallery"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/gallery/([^/?#]+)/?$"
    example = "https://piczel.tv/gallery/USER"

    def posts(self):
        url = "{}/api/users/{}/gallery".format(self.root_api, self.groups[0])
        return self._pagination(url)


class PiczelFolderExtractor(PiczelExtractor):
    """Extractor for images inside a user's folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user[username]}", "{folder[name]}")
    archive_fmt = "f{folder[id]}_{id}_{num}"
    pattern = BASE_PATTERN + r"/gallery/(?!image/)[^/?#]+/(\d+)"
    example = "https://piczel.tv/gallery/USER/12345"

    def posts(self):
        url = "{}/api/gallery/folder/{}".format(self.root_api, self.groups[0])
        return self._pagination(url)


class PiczelImageExtractor(PiczelExtractor):
    """Extractor for individual images"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/gallery/image/(\d+)"
    example = "https://piczel.tv/gallery/image/12345"

    def posts(self):
        url = "{}/api/gallery/{}".format(self.root_api, self.groups[0])
        return (self.request(url).json(),)
