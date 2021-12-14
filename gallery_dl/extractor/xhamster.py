# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://xhamster.com/"""

from .common import Extractor, Message
from .. import text
import json


BASE_PATTERN = (r"(?:https?://)?((?:[\w-]+\.)?xhamster"
                r"(?:\d?\.(?:com|one|desi)|\.porncache\.net))")


class XhamsterExtractor(Extractor):
    """Base class for xhamster extractors"""
    category = "xhamster"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = "https://" + match.group(1)


class XhamsterGalleryExtractor(XhamsterExtractor):
    """Extractor for image galleries on xhamster.com"""
    subcategory = "gallery"
    directory_fmt = ("{category}", "{user[name]}",
                     "{gallery[id]} {gallery[title]}")
    filename_fmt = "{num:>03}_{id}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"(/photos/gallery/[^/?#]+)"
    test = (
        ("https://xhamster.com/photos/gallery/11748968", {
            "pattern": r"https://thumb-p\d+.xhcdn.com/./[\w/-]+_1000.jpg$",
            "count": ">= 144",
            "keyword": {
                "comments": int,
                "count": int,
                "favorite": bool,
                "id": int,
                "num": int,
                "height": int,
                "width": int,
                "imageURL": str,
                "pageURL": str,
                "thumbURL": str,
                "gallery": {
                    "date": "dt:2019-04-16 00:07:31",
                    "description": "",
                    "dislikes": int,
                    "id": 11748968,
                    "likes": int,
                    "tags": ["NON-Porn"],
                    "thumbnail": str,
                    "title": "Make the world better.",
                    "views": int,
                },
                "user": {
                    "id": 16874672,
                    "name": "Anonymousrants",
                    "retired": bool,
                    "subscribers": int,
                    "url": "https://xhamster.com/users/anonymousrants",
                    "verified": bool,
                },
            },
        }),
        ("https://jp.xhamster2.com/photos/gallery/11748968", {
            "pattern": r"https://thumb-p\d+.xhcdn.com/./[\w/-]+_1000.jpg$",
            "count": ">= 144",
        }),
        ("https://xhamster.com/photos/gallery/make-the-world-better-11748968"),
        ("https://xhamster.com/photos/gallery/11748968"),
        ("https://xhamster.one/photos/gallery/11748968"),
        ("https://xhamster.desi/photos/gallery/11748968"),
        ("https://xhamster2.com/photos/gallery/11748968"),
        ("https://en.xhamster.com/photos/gallery/11748968"),
        ("https://xhamster.porncache.net/photos/gallery/11748968"),
    )

    def __init__(self, match):
        XhamsterExtractor.__init__(self, match)
        self.path = match.group(2)
        self.data = None

    def items(self):
        data = self.metadata()
        yield Message.Directory, data
        for num, image in enumerate(self.images(), 1):
            url = image["imageURL"]
            image.update(data)
            image["num"] = num
            yield Message.Url, url, text.nameext_from_url(url, image)

    def metadata(self):
        self.data = self._data(self.root + self.path)
        user = self.data["authorModel"]
        imgs = self.data["photosGalleryModel"]

        return {
            "user":
            {
                "id"         : text.parse_int(user["id"]),
                "url"        : user["pageURL"],
                "name"       : user["name"],
                "retired"    : user["retired"],
                "verified"   : user["verified"],
                "subscribers": user["subscribers"],
            },
            "gallery":
            {
                "id"         : text.parse_int(imgs["id"]),
                "tags"       : [c["name"] for c in imgs["categories"]],
                "date"       : text.parse_timestamp(imgs["created"]),
                "views"      : text.parse_int(imgs["views"]),
                "likes"      : text.parse_int(imgs["rating"]["likes"]),
                "dislikes"   : text.parse_int(imgs["rating"]["dislikes"]),
                "title"      : text.unescape(imgs["title"]),
                "description": text.unescape(imgs["description"]),
                "thumbnail"  : imgs["thumbURL"],
            },
            "count": text.parse_int(imgs["quantity"]),
        }

    def images(self):
        data = self.data
        self.data = None

        while True:
            for image in data["photosGalleryModel"]["photos"]:
                del image["modelName"]
                yield image

            pgntn = data["pagination"]
            if pgntn["active"] == pgntn["maxPage"]:
                return
            url = pgntn["pageLinkTemplate"][:-3] + str(pgntn["next"])
            data = self._data(url)

    def _data(self, url):
        page = self.request(url).text
        return json.loads(text.extract(
            page, "window.initials=", "</script>")[0].rstrip("\n\r;"))


class XhamsterUserExtractor(XhamsterExtractor):
    """Extractor for all galleries of an xhamster user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/users/([^/?#]+)(?:/photos)?/?(?:$|[?#])"
    test = (
        ("https://xhamster.com/users/goldenpalomino/photos", {
            "pattern": XhamsterGalleryExtractor.pattern,
            "count": 50,
            "range": "1-50",
        }),
        ("https://xhamster.com/users/nickname68"),
    )

    def __init__(self, match):
        XhamsterExtractor.__init__(self, match)
        self.user = match.group(2)

    def items(self):
        url = "{}/users/{}/photos".format(self.root, self.user)
        data = {"_extractor": XhamsterGalleryExtractor}

        while url:
            extr = text.extract_from(self.request(url).text)
            while True:
                url = extr('thumb-image-container role-pop" href="', '"')
                if not url:
                    break
                yield Message.Queue, url, data
            url = extr('data-page="next" href="', '"')
