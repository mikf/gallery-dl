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
    """Extractor for albums on slideshare.net"""
    category = "photobucket"
    subcategory = "album"
    directory_fmt = ["{category}", "{username}", "{location}"]
    filename_fmt = "{offset:>03}_{pictureId}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = [r"(?:https?://)?(?:[^.]+\.)?photobucket\.com"
               r"/user/[^/?&#]+/library/[^?&#]*"]
    test = [
        ("http://s258.photobucket.com/user/focolandia/library/", {
            "pattern": r"http://i\d+.photobucket.com/albums/hh280/focolandia",
            "count": ">= 39"
        }),
        ("http://s1110.photobucket.com/user/chndrmhn100/library/"
         "Chandu%20is%20the%20King?sort=3&page=1", None),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(0)

    def items(self):
        # prevent watermarks
        self.session.headers["Referer"] = self.url

        yield Message.Version, 1
        for image in self.images():
            image["title"] = text.unescape(image["title"])
            image["extension"] = image["ext"]
            yield Message.Directory, image
            yield Message.Url, image["fullsizeUrl"], image

    def images(self):
        params = {"sort": "3", "page": 1}
        return self._pagination(self.url, params)

    def _pagination(self, url, params):
        while True:
            page = self.request(url, params=params).text
            data = json.loads(text.extract(page, "collectionData:", ",\n")[0])

            yield from data["items"]["objects"]

            if data["total"] <= data["offset"] + data["pageSize"]:
                return
            params["page"] += 1
