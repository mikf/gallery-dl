# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://photobucket.com/"""

from .common import Extractor, Message
from .. import text
import json


class PhotobucketAlbumExtractor(Extractor):
    """Extractor for albums on photobucket.com"""
    category = "photobucket"
    subcategory = "album"
    directory_fmt = ["{category}", "{username}", "{location}"]
    filename_fmt = "{offset:>03}{pictureId:?_//}_{titleOrFilename}.{extension}"
    archive_fmt = "{id}"
    pattern = [r"(?:https?://)?((?:[^.]+\.)?photobucket\.com)"
               r"/user/[^/?&#]+/library/[^?&#]*"]
    test = [
        ("http://s258.photobucket.com/user/focolandia/library/", {
            "pattern": r"http://i\d+.photobucket.com/albums/hh280/focolandia",
            "count": ">= 39"
        }),
        ("http://s271.photobucket.com/user/lakerfanryan/library/", {
            "options": (("image-filter", "False"),),
            "pattern": "http://s271.photobucket.com/user/lakerfanryan/library",
            "count": ">= 22",
        }),
        ("http://s1110.photobucket.com/user/chndrmhn100/library/"
         "Chandu%20is%20the%20King?sort=3&page=1", None),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.album_path = ""
        self.url = match.group(0)
        self.root = "http://" + match.group(1)
        self.session.headers["Referer"] = self.url

    def items(self):
        yield Message.Version, 1
        for image in self.images():
            image["titleOrFilename"] = text.unescape(image["titleOrFilename"])
            image["title"] = text.unescape(image["title"])
            image["extension"] = image["ext"]
            yield Message.Directory, image
            yield Message.Url, image["fullsizeUrl"], image

        if self.config("subalbums", True):
            for album in self.subalbums():
                yield Message.Queue, album["url"], album

    def images(self):
        """Yield all images of the current album"""
        url = self.url
        params = {"sort": "3", "page": 1}

        while True:
            page = self.request(url, params=params).text
            data = json.loads(text.extract(page, "collectionData:", ",\n")[0])

            yield from data["items"]["objects"]

            if data["total"] <= data["offset"] + data["pageSize"]:
                self.album_path = data["currentAlbumPath"]
                return
            params["page"] += 1

    def subalbums(self):
        """Yield all subalbum URLs"""
        url = self.root + "/component/Albums-SubalbumList"
        params = {"albumPath": self.album_path, "json": "1"}

        data = self.request(url, params=params).json()
        albums = data["body"]["subAlbums"]
        albums.reverse()

        while albums:
            album = albums.pop()

            subs = album.pop("subAlbums")
            if subs:
                subs.reverse()
                albums.extend(subs)

            yield album
