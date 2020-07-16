# -*- coding: utf-8 -*-

# Copyright 2017-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gfycat.com/"""

from .common import Extractor, Message


class GfycatExtractor(Extractor):
    """Base class for gfycat extractors"""
    category = "gfycat"
    filename_fmt = "{category}_{gfyName}{title:?_//}.{extension}"
    archive_fmt = "{gfyName}"
    root = "https://gfycat.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.key = match.group(1)
        self.formats = (self.config("format", "mp4"), "mp4", "webm", "gif")

    def items(self):
        metadata = self.metadata()
        for gfycat in self.gfycats():
            url = self._select_format(gfycat)
            gfycat.update(metadata)
            yield Message.Directory, gfycat
            yield Message.Url, url, gfycat

    def _select_format(self, gfyitem):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gfyitem:
                url = gfyitem[key]
                gfyitem["extension"] = url.rpartition(".")[2]
                return url
        return ""

    def metadata(self):
        return {}

    def gfycats(self):
        return ()


class GfycatImageExtractor(GfycatExtractor):
    """Extractor for individual images from gfycat.com"""
    subcategory = "image"
    pattern = (r"(?:https?://)?(?:\w+\.)?gfycat\.com"
               r"/(?:gifs/detail/|\w+/)?([A-Za-z]+)")
    test = (
        ("https://gfycat.com/GrayGenerousCowrie", {
            "url": "e0b5e1d7223108249b15c3c7898dd358dbfae045",
            "content": "5786028e04b155baa20b87c5f4f77453cd5edc37",
            "keyword": {
                "gfyId": "graygenerouscowrie",
                "gfyName": "GrayGenerousCowrie",
                "gfyNumber": "755075459",
                "title": "Bottom's up",
                "userName": "jackson3oh3",
                "createDate": 1495884169,
                "md5": "a4796e05b0db9ba9ce5140145cd318aa",
                "width": 400,
                "height": 224,
                "frameRate": 23,
                "numFrames": 158,
                "views": int,
            },
        }),
        (("https://thumbs.gfycat.com/SillyLameIsabellinewheatear"
          "-size_restricted.gif"), {
            "url": "13b32e6cc169d086577d7dd3fd36ee6cdbc02726",
        }),
        ("https://gfycat.com/detail/UnequaledHastyAnkole?tagname=aww", {
            "url": "e24c9f69897fd223343782425a429c5cab6a768e",
        }),
        ("https://gfycat.com/gifs/detail/UnequaledHastyAnkole"),
        ("https://gfycat.com/ifr/UnequaledHastyAnkole"),
        ("https://gfycat.com/ru/UnequaledHastyAnkole"),
    )

    def gfycats(self):
        url = "https://api.gfycat.com/v1/gfycats/" + self.key
        return (self.request(url).json()["gfyItem"],)
