# -*- coding: utf-8 -*-

# Copyright 2018-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://piczel.tv/"""

from .common import Extractor, Message
from .. import text


class PiczelExtractor(Extractor):
    """Base class for piczel extractors"""
    category = "piczel"
    directory_fmt = ("{category}", "{user[username]}")
    filename_fmt = "{category}_{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    root = "https://piczel.tv"
    api_root = "https://tombstone.piczel.tv"

    def items(self):
        yield Message.Version, 1
        for post in self.posts():
            post["tags"] = [t["title"] for t in post["tags"] if t["title"]]
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            if post["multi"]:
                images = post["images"]
                del post["images"]
                yield Message.Directory, post
                for post["num"], image in enumerate(images):
                    if "id" in image:
                        del image["id"]
                    post.update(image)
                    url = post["image"]["url"]
                    yield Message.Url, url, text.nameext_from_url(url, post)

            else:
                yield Message.Directory, post
                post["num"] = 0
                url = post["image"]["url"]
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        """Return an iterable with all relevant post objects"""

    def _pagination(self, url, folder_id=None):
        params = {
            "from_id"  : None,
            "folder_id": folder_id,
        }

        while True:
            data = self.request(url, params=params).json()
            if not data:
                return
            params["from_id"] = data[-1]["id"]

            for post in data:
                if not folder_id or folder_id == post["folder_id"]:
                    yield post


class PiczelUserExtractor(PiczelExtractor):
    """Extractor for all images from a user's gallery"""
    subcategory = "user"
    pattern = r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/([^/?#]+)/?$"
    test = ("https://piczel.tv/gallery/Bikupan", {
        "range": "1-100",
        "count": ">= 100",
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.user = match.group(1)

    def posts(self):
        url = "{}/api/users/{}/gallery".format(self.api_root, self.user)
        return self._pagination(url)


class PiczelFolderExtractor(PiczelExtractor):
    """Extractor for images inside a user's folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user[username]}", "{folder[name]}")
    archive_fmt = "f{folder[id]}_{id}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?piczel\.tv"
               r"/gallery/(?!image)([^/?#]+)/(\d+)")
    test = ("https://piczel.tv/gallery/Lulena/1114", {
        "count": ">= 4",
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.user, self.folder_id = match.groups()

    def posts(self):
        url = "{}/api/users/{}/gallery".format(self.api_root, self.user)
        return self._pagination(url, int(self.folder_id))


class PiczelImageExtractor(PiczelExtractor):
    """Extractor for individual images"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/image/(\d+)"
    test = ("https://piczel.tv/gallery/image/7807", {
        "pattern": r"https://(\w+\.)?piczel\.tv/static/uploads/gallery_image"
                   r"/32920/image/7807/25737334-Lulena\.png",
        "content": "df9a053a24234474a19bce2b7e27e0dec23bff87",
        "keyword": {
            "created_at": "2018-07-22T05:13:58.000Z",
            "date": "dt:2018-07-22 05:13:58",
            "description": None,
            "extension": "png",
            "favorites_count": int,
            "folder": dict,
            "folder_id": 1113,
            "id": 7807,
            "is_flash": False,
            "is_video": False,
            "multi": False,
            "nsfw": False,
            "num": 0,
            "password_protected": False,
            "tags": ["fanart", "commission", "altair", "recreators"],
            "title": "Altair",
            "user": dict,
            "views": int,
        },
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def posts(self):
        url = "{}/api/gallery/{}".format(self.api_root, self.image_id)
        return (self.request(url).json(),)
