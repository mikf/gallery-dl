# -*- coding: utf-8 -*-

# Copyright 2018-2019 Mike Fährmann
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

    def items(self):
        yield Message.Version, 1
        for image in self.unpack(self.images()):
            url = self.root + "/static" + image["image"]["image"]["url"]
            yield Message.Directory, image
            yield Message.Url, url, text.nameext_from_url(url, image)

    @staticmethod
    def unpack(images):
        """Unpack 'images' into individual image objects"""
        for image in images:
            if image["multi"]:
                multi = image["images"]
                del image["images"]
                for image["num"], img in enumerate(multi):
                    image["image"] = img
                    yield image
            else:
                image["num"] = 0
                yield image

    def images(self):
        """Return an iterable with all relevant image objects"""

    def _pagination(self, url, folder_id=None):
        params = {
            "hideNsfw" : "false",
            "from_id"  : None,
            "folder_id": folder_id,
        }

        while True:
            data = self.request(url, params=params).json()
            yield from data

            if len(data) < 32:
                return
            params["from_id"] = data[-1]["id"]


class PiczelUserExtractor(PiczelExtractor):
    """Extractor for all images from a user's gallery"""
    subcategory = "user"
    pattern = r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/([^/?&#]+)/?$"
    test = ("https://piczel.tv/gallery/Maximumwarp", {
        "count": ">= 50",
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.user = match.group(1)

    def images(self):
        url = "{}/api/users/{}/gallery".format(self.root, self.user)
        return self._pagination(url)


class PiczelFolderExtractor(PiczelExtractor):
    """Extractor for images inside a user's folder"""
    subcategory = "folder"
    directory_fmt = ("{category}", "{user[username]}", "{folder[name]}")
    archive_fmt = "f{folder[id]}_{id}_{num}"
    pattern = (r"(?:https?://)?(?:www\.)?piczel\.tv"
               r"/gallery/(?!image)([^/?&#]+)/(\d+)")
    test = ("https://piczel.tv/gallery/Lulena/1114", {
        "count": ">= 4",
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.user, self.folder_id = match.groups()

    def images(self):
        url = "{}/api/users/{}/gallery".format(self.root, self.user)
        return self._pagination(url, self.folder_id)


class PiczelImageExtractor(PiczelExtractor):
    """Extractor for individual images"""
    subcategory = "image"
    pattern = r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/image/(\d+)"
    test = ("https://piczel.tv/gallery/image/7807", {
        "url": "85225dd53a03c3b6028f6c4a45b71eccc07f7066",
        "content": "df9a053a24234474a19bce2b7e27e0dec23bff87",
        "keyword": {
            "created_at": "2018-07-22T05:13:58.000Z",
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
            "tags": "fanart, commission, altair, recreators, ",
            "title": "Altair",
            "user": dict,
            "views": int,
        },
    })

    def __init__(self, match):
        PiczelExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def images(self):
        url = "{}/api/gallery/image/{}".format(self.root, self.image_id)
        return (self.request(url).json(),)
