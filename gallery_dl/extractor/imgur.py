# -*- coding: utf-8 -*-

# Copyright 2015-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://imgur.com/"""

from .common import Extractor, Message
from .. import text, exception
import itertools
import json


BASE_PATTERN = r"(?:https?://)?(?:www\.|[im]\.)?imgur\.com"


class ImgurExtractor(Extractor):
    """Base class for imgur extractors"""
    category = "imgur"
    root = "https://imgur.com"
    api_root = "https://api.imgur.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)
        self.mp4 = self.config("mp4", True)

    def _extract_data(self, path):
        response = self.request(self.root + path, notfound=self.subcategory)
        data = json.loads(text.extract(
            response.text, "image               : ", ",\n")[0])
        try:
            del data["adConfig"]
            del data["isAd"]
        except KeyError:
            pass
        return data

    def _prepare(self, image):
        image["ext"] = image["ext"].partition("?")[0]
        if image["ext"] == ".gif" and (
                (self.mp4 and image["prefer_video"]) or self.mp4 == "always"):
            image["ext"] = ".mp4"
        url = "https://i.imgur.com/" + image["hash"] + image["ext"]
        image["extension"] = image["ext"][1:]
        return url

    def _items_apiv3(self, urlfmt):
        album_ex = ImgurAlbumExtractor
        image_ex = ImgurImageExtractor

        params = {
            "IMGURPLATFORM" : "web",
            "album_previews": "0",
            "client_id"     : "546c25a59c58ad7",
        }
        headers = {
            "Origin" : self.root,
            "Referer": self.root + "/",
        }

        yield Message.Version, 1

        for num in itertools.count(0):
            url = urlfmt.format(num)
            data = self.request(url, params=params, headers=headers).json()

            for item in data["data"]:
                item["_extractor"] = album_ex if item["is_album"] else image_ex
                yield Message.Queue, item["link"], item

            if len(data["data"]) < 60:
                return


class ImgurImageExtractor(ImgurExtractor):
    """Extractor for individual images on imgur.com"""
    subcategory = "image"
    filename_fmt = "{category}_{hash}{title:?_//}.{extension}"
    archive_fmt = "{hash}"
    pattern = BASE_PATTERN + r"/(?!gallery)(\w{7}|\w{5})[sbtmlh]?\.?"
    test = (
        ("https://imgur.com/21yMxCS", {
            "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
            "content": "0c8768055e4e20e7c7259608b67799171b691140",
            "keyword": {
                "animated": False,
                "datetime": "2016-11-10 14:24:35",
                "description": str,
                "ext": ".png",
                "extension": "png",
                "hash": "21yMxCS",
                "height": "32",
                "is_moderated": False,
                "is_safe": False,
                "is_viral": 0,
                "looping": False,
                "mimetype": "image/png",
                "name": None,
                "prefer_video": False,
                "size": 182,
                "source": "",
                "title": "Test",
                "video_host": None,
                "video_source": None,
                "width": "64",
            },
        }),
        ("http://imgur.com/0gybAXR", {  # gifv/mp4 video
            "url": "a2220eb265a55b0c95e0d3d721ec7665460e3fd7",
            "content": "a3c080e43f58f55243ab830569ba02309d59abfc",
        }),
        ("https://imgur.com/HjoXJAd", {  # url ends with '.jpg?1'
            "url": "73f361b50753ab25da64160aa50bc5d139480d45",
        }),
        ("https://imgur.com/zzzzzzz", {  # not found
            "exception": exception.NotFoundError,
        }),
        ("https://www.imgur.com/21yMxCS"),  # www
        ("https://m.imgur.com/21yMxCS"),  # mobile
        ("https://imgur.com/zxaY6"),  # 5 character key
        ("https://i.imgur.com/21yMxCS.png"),  # direct link
        ("https://i.imgur.com/21yMxCSh.png"),  # direct link thumbnail
        ("https://i.imgur.com/zxaY6.gif"),  # direct link (short)
        ("https://i.imgur.com/zxaY6s.gif"),  # direct link (short; thumb)
    )

    def items(self):
        image = self._extract_data("/" + self.key)
        url = self._prepare(image)
        yield Message.Version, 1
        yield Message.Directory, image
        yield Message.Url, url, image


class ImgurAlbumExtractor(ImgurExtractor):
    """Extractor for imgur albums"""
    subcategory = "album"
    directory_fmt = ("{category}", "{album[hash]}{album[title]:? - //}")
    filename_fmt = "{category}_{album[hash]}_{num:>03}_{hash}.{extension}"
    archive_fmt = "{album[hash]}_{hash}"
    pattern = BASE_PATTERN + r"/(?:a|t/unmuted)/(\w{7}|\w{5})"
    test = (
        ("https://imgur.com/a/TcBmP", {
            "url": "ce3552f550a5b5316bd9c7ae02e21e39f30c0563",
            "keyword": {
                "album": {
                    "album_cover": "693j2Kr",
                    "album_description": None,
                    "cover": "693j2Kr",
                    "datetime": "2015-10-09 10:37:50",
                    "description": None,
                    "hash": "TcBmP",
                    "id": "TcBmP",
                    "is_album": True,
                    "num_images": "19",
                    "title": "138",
                    "title_clean": "TcBmP",
                    "views": str,
                },
                "animated": bool,
                "datetime": str,
                "extension": str,
                "hash": str,
                "height": int,
                "num": int,
                "prefer_video": bool,
                "size": int,
                "title": str,
                "width": int,
            },
        }),
        ("https://imgur.com/a/eD9CT", {  # large album
            "url": "4ee94de31ff26be416271bc0b1ea27b9349c9937",
        }),
        ("https://imgur.com/a/RhJXhVT/all", {  # 7 character album hash
            "url": "695ef0c950023362a0163ee5041796300db76674",
        }),
        ("https://imgur.com/t/unmuted/YMqBcua", {  # unmuted URL
            "url": "86b4747f8147cec7602f0214e267309af73a8655",
        }),
        ("https://imgur.com/a/TcBmQ", {
            "exception": exception.NotFoundError,
        }),
        ("https://www.imgur.com/a/TcBmP"),  # www
        ("https://m.imgur.com/a/TcBmP"),  # mobile
    )

    def items(self):
        album = self._extract_data("/a/" + self.key + "/all")
        images = album["album_images"]["images"]
        del album["album_images"]

        if int(album["num_images"]) > len(images):
            url = "{}/ajaxalbums/getimages/{}/hit.json".format(
                self.root, self.key)
            images = self.request(url).json()["data"]["images"]

        yield Message.Version, 1
        yield Message.Directory, {"album": album, "count": len(images)}
        for num, image in enumerate(images, 1):
            url = self._prepare(image)
            image["num"] = num
            image["album"] = album
            yield Message.Url, url, image


class ImgurGalleryExtractor(ImgurExtractor):
    """Extractor for imgur galleries"""
    subcategory = "gallery"
    pattern = BASE_PATTERN + r"/gallery/(\w{7}|\w{5})"
    test = (
        ("https://imgur.com/gallery/zf2fIms", {  # non-album gallery (#380)
            "pattern": "https://imgur.com/zf2fIms",
        }),
        ("https://imgur.com/gallery/eD9CT", {
            "pattern": "https://imgur.com/a/eD9CT",
        }),
    )

    def items(self):
        url = self.root + "/a/" + self.key
        with self.request(url, method="HEAD", fatal=False) as response:
            code = response.status_code

        if code < 400:
            extr = ImgurAlbumExtractor
        else:
            extr = ImgurImageExtractor
            url = self.root + "/" + self.key

        yield Message.Version, 1
        yield Message.Queue, url, {"_extractor": extr}


class ImgurUserExtractor(ImgurExtractor):
    """Extractor for all images posted by a user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)(?:/posts|/submitted)?/?$"
    test = (
        ("https://imgur.com/user/Miguenzo", {
            "range": "1-100",
            "count": 100,
            "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
        }),
        ("https://imgur.com/user/Miguenzo/posts"),
        ("https://imgur.com/user/Miguenzo/submitted"),
    )

    def items(self):
        urlfmt = "{}/3/account/{}/submissions/{{}}/newest".format(
            self.api_root, self.key)
        return self._items_apiv3(urlfmt)


class ImgurFavoriteExtractor(ImgurExtractor):
    """Extractor for a user's favorites"""
    subcategory = "favorite"
    pattern = BASE_PATTERN + r"/user/([^/?&#]+)/favorites"
    test = ("https://imgur.com/user/Miguenzo/favorites", {
        "range": "1-100",
        "count": 100,
        "pattern": r"https?://(i.imgur.com|imgur.com/a)/[\w.]+",
    })

    def items(self):
        urlfmt = "{}/3/account/{}/gallery_favorites/{{}}/newest".format(
            self.api_root, self.key)
        return self._items_apiv3(urlfmt)
