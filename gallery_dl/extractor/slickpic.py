# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.slickpic.com/"""

from .common import Extractor, Message
from .. import text
import time


BASE_PATTERN = r"(?:https?://)?([^.]+)\.slickpic\.com"


class SlickpicExtractor(Extractor):
    """Base class for slickpic extractors"""
    category = "slickpic"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.root = "https://{}.slickpic.com".format(self.user)


class SlickpicAlbumExtractor(SlickpicExtractor):
    """Extractor for albums on slickpic.com"""
    subcategory = "album"
    directory_fmt = ("{category}", "{user[name]}",
                     "{album[id]} {album[title]}")
    filename_fmt = "{num:>03}_{id}{title:?_//}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/albums/([^/?&#]+)"
    test = (
        ("https://mattcrandall.slickpic.com/albums/LamborghiniMurcielago/", {
            "url": "58bd94ebc80fd906e9879826970b408d54c6da07",
            "keyword": "54a9d6f9e42ae43c644aa9316186fb9d9955fe53",
        }),
        ("https://mattcrandall.slickpic.com/albums/LamborghiniMurcielago/", {
            "range": "34",
            "content": ("cec6630e659dc72db1ee1a9a6f3b525189261988",
                        "6f81e1e74c6cd6db36844e7211eef8e7cd30055d",
                        "22e83645fc242bc3584eca7ec982c8a53a4d8a44"),
        }),
    )

    def __init__(self, match):
        SlickpicExtractor.__init__(self, match)
        self.album = match.group(2)

    def items(self):
        data = self.metadata()
        imgs = self.images(data)

        data = {
            "album": {
                "id"   : text.parse_int(data["aid"]),
                "title": text.unescape(data["title"]),
            },
            "user": {
                "id"  : text.parse_int(data["uid"]),
                "name": text.unescape(data["user"]),
                "nick": self.user
            },
            "count": len(imgs),
        }

        yield Message.Version, 1
        yield Message.Directory, data
        for num, img in enumerate(imgs, 1):
            url = img["url_rsz"] + "/o/" + img["fname"]
            img = text.nameext_from_url(img["fname"], {
                "url"        : url,
                "num"        : num,
                "id"         : text.parse_int(img["id"]),
                "width"      : text.parse_int(img["width"]),
                "height"     : text.parse_int(img["height"]),
                "title"      : img["title"],
                "description": img["descr"],
            })
            img.update(data)
            yield Message.Url, url, img

    def metadata(self):
        url = "{}/albums/{}/?wallpaper".format(self.root, self.album)
        extr = text.extract_from(self.request(url).text)

        title = text.unescape(extr("<title>", "</title>"))
        title, _, user = title.rpartition(" by ")

        return {
            "title": title,
            "user" : user,
            "tk"   : extr('tk = "', '"'),
            "shd"  : extr('shd = "', '"'),
            "aid"  : extr('data-aid="', '"', ),
            "uid"  : extr('data-uid="', '"', ),
        }

    def images(self, data):
        url = self.root + "/xhr/photo/get/list"
        data = {
            "tm"    : time.time(),
            "tk"    : data["tk"],
            "shd"   : data["shd"],
            "aid"   : data["aid"],
            "uid"   : data["uid"],
            "col"   : "0",
            "sys"   : self.album,
            "vw"    : "1280",
            "vh"    : "1024",
            "skey"  : "",
            "viewer": "false",
            "pub"   : "1",
            "sng"   : "0",
            "whq"   : "1",
        }
        return self.request(url, method="POST", data=data).json()["list"]


class SlickpicUserExtractor(SlickpicExtractor):
    subcategory = "user"
    pattern = BASE_PATTERN + r"(?:/gallery)?/?(?:$|[?#])"
    test = (
        ("https://mattcrandall.slickpic.com/gallery/", {
            "count": ">= 358",
            "pattern": SlickpicAlbumExtractor.pattern,
        }),
        ("https://mattcrandall.slickpic.com/"),
    )

    def items(self):
        page = self.request(self.root + "/gallery?viewer").text
        data = {"_extractor": SlickpicAlbumExtractor}
        base = self.root + "/albums/"

        yield Message.Version, 1
        for album in text.extract_iter(page, 'href="' + base, '"'):
            yield Message.Queue, base + album, data
