# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://imgbb.com/"""

from .common import Extractor, Message
from .. import text
import json


class ImgbbAlbumExtractor(Extractor):
    """Extractor for albums on imgbb.com"""
    category = "imgbb"
    subcategory = "album"
    root = "https://imgbb.com"
    directory_fmt = ("{category}", "{user[username]}",
                     "{album_id} {album_name}")
    filename_fmt = "{id}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = r"(?:https?://)?ibb\.co/album/([^/?&#]+)(?:\?([^#]+))?"
    test = ("https://ibb.co/album/c6p5Yv", {
        "range": "1-100",
        "url": "",
        "keyword": "",
    })

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.album_id = match.group(1)
        self.album_name = None
        self.params = text.parse_query(match.group(2))

    def items(self):
        first = True
        yield Message.Version, 1

        for img in self.images():
            url = img["image"]["url"]
            img["album_id"] = self.album_id
            img["album_name"] = self.album_name
            img["id"] = img["url_viewer"].rpartition("/")[2]
            if first:
                first = False
                yield Message.Directory, img
            yield Message.Url, url, img

    def images(self):
        url = "https://ibb.co/album/" + self.album_id
        page = self.request(url).text

        self.album_name, pos = text.extract(page, '"og:title" content="', '"')
        seek, pos = text.extract(page, 'data-seek="', '"', pos)
        tokn, pos = text.extract(page, 'PF.obj.config.auth_token="', '"', pos)

        endpoint = "https://ibb.co/json"
        data = None
        params = {
            "action" : "list",
            "list"   : "images",
            "from"   : "album",
            "sort"   : "date_desc",
            "page"   : 2,
            "albumid": self.album_id,
            "params_hidden[list]"   : "images",
            "params_hidden[from]"   : "album",
            "params_hidden[albumid]": self.album_id,
            "seek"      : seek,
            "auth_token": tokn,
        }

        while True:
            for img in text.extract_iter(page, "data-object='", "'"):
                yield json.loads(text.unquote(img))
            if data:
                if params["seek"] == data["seekEnd"]:
                    return
                params["seek"] = data["seekEnd"]
                params["page"] += 1
            data = self.request(endpoint, "POST", data=params).json()
            page = data["html"]
