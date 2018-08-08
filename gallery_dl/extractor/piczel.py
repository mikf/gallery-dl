# -*- coding: utf-8 -*-

# Copyright 2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://piczel.tv/"""

from .common import Extractor, Message
from .. import text


class PiczelExtractor(Extractor):
    """Base class for piczel extractors"""
    category = "piczel"
    directory_fmt = ["{category}", "{user[username]}"]
    filename_fmt = "{category}_{id}_{title}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    root = "https://piczel.tv"
    api_root = "https://apollo.piczel.tv"

    def __init__(self, match):
        Extractor.__init__(self)
        self.item_id = match.group(1)

    def items(self):
        first = True
        yield Message.Version, 1
        for image in self.unpack(self.get_images()):
            if first:
                yield Message.Directory, image
                first = False
            path = image["image"]["image"]["url"]
            url = "{}/static/{}".format(self.api_root, path)
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

    def get_images(self):
        """Return an iterable with all relevant image objects"""


class PiczelUserExtractor(PiczelExtractor):
    """Extractor for all images from a user's gallery"""
    subcategory = "user"
    pattern = [r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/([^/?&#]+)/?$"]
    test = [("https://piczel.tv/gallery/Lulena", {
        "count": ">= 13",
    })]

    def get_images(self):
        url = "{}/api/users/{}/gallery".format(self.api_root, self.item_id)
        return self.request(url).json()


class PiczelFolderExtractor(PiczelExtractor):
    """Extractor for images inside a user's folder"""
    subcategory = "folder"
    directory_fmt = ["{category}", "{user[username]}", "{folder[name]}"]
    archive_fmt = "f{folder[id]}_{id}_{num}"
    pattern = [r"(?:https?://)?(?:www\.)?piczel\.tv"
               r"/gallery/(?!image)[^/?&#]+/(\d+)"]
    test = [("https://piczel.tv/gallery/Lulena/1114", {
        "count": ">= 4",
    })]

    def get_images(self):
        url = "{}/api/gallery/folder/{}".format(self.api_root, self.item_id)
        images = self.request(url).json()
        images.reverse()
        return images


class PiczelImageExtractor(PiczelExtractor):
    """Extractor for individual images"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?piczel\.tv/gallery/image/(\d+)"]
    test = [("https://piczel.tv/gallery/image/7807", {
        "url": "c8caccac9fa798dc4fd4b920890e4d8b42cb44e5",
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
    })]

    def get_images(self):
        url = "{}/api/gallery/image/{}".format(self.api_root, self.item_id)
        return (self.request(url).json(),)
