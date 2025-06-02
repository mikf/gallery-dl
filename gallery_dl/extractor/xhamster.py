# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://xhamster.com/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = (r"(?:https?://)?((?:[\w-]+\.)?xhamster"
                r"(?:\d?\.(?:com|one|desi)|\.porncache\.net))")


class XhamsterExtractor(Extractor):
    """Base class for xhamster extractors"""
    category = "xhamster"

    def __init__(self, match):
        self.root = "https://" + match.group(1)
        Extractor.__init__(self, match)


class XhamsterGalleryExtractor(XhamsterExtractor):
    """Extractor for image galleries on xhamster.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[name]}",
                     "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"(/photos/gallery/[^/?#]+)"
    example = "https://xhamster.com/photos/gallery/12345"

    def items(self):
        data = self.metadata()
        yield Message.Directory, data
        for num, image in enumerate(self.images(), 1):
            url = image["imageURL"]
            image.update(data)
            text.nameext_from_url(url, image)
            image["num"] = num
            image["extension"] = "webp"
            del image["modelName"]
            yield Message.Url, url, image

    def metadata(self):
        data = self.data = self._extract_data(self.root + self.groups[1])

        gallery = data["galleryPage"]
        info = gallery["infoProps"]
        model = gallery["galleryModel"]
        author = info["authorInfoProps"]

        return {
            "user":
            {
                "id"         : text.parse_int(model["userId"]),
                "url"        : author["authorLink"],
                "name"       : author["authorName"],
                "verified"   : True if author.get("verified") else False,
                "subscribers": info["subscribeButtonProps"]["subscribers"],
            },
            "gallery":
            {
                "id"         : text.parse_int(gallery["id"]),
                "tags"       : [t["label"] for t in info["categoriesTags"]],
                "date"       : text.parse_timestamp(model["created"]),
                "views"      : text.parse_int(model["views"]),
                "likes"      : text.parse_int(model["rating"]["likes"]),
                "dislikes"   : text.parse_int(model["rating"]["dislikes"]),
                "title"      : model["title"],
                "description": model["description"],
                "thumbnail"  : model["thumbURL"],
            },
            "count": text.parse_int(gallery["photosCount"]),
        }

    def images(self):
        data = self.data
        self.data = None

        while True:
            yield from data["photosGalleryModel"]["photos"]

            pagination = data["galleryPage"]["paginationProps"]
            if pagination["currentPageNumber"] >= pagination["lastPageNumber"]:
                return
            url = (pagination["pageLinkTemplate"][:-3] +
                   str(pagination["currentPageNumber"] + 1))

            data = self._extract_data(url)

    def _extract_data(self, url):
        page = self.request(url).text
        return util.json_loads(text.extr(
            page, "window.initials=", "</script>").rstrip("\n\r;"))


class XhamsterUserExtractor(XhamsterExtractor):
    """Extractor for all galleries of an xhamster user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/users/([^/?#]+)(?:/photos)?/?(?:$|[?#])"
    example = "https://xhamster.com/users/USER/photos"

    def items(self):
        url = "{}/users/{}/photos".format(self.root, self.groups[1])
        data = {"_extractor": XhamsterGalleryExtractor}

        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                url = extr('thumb-image-container role-pop" href="', '"')
                if not url:
                    break
                yield Message.Queue, url, data
            url = extr('data-page="next" href="', '"')
