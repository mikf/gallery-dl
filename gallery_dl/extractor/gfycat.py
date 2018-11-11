# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://gfycat.com/"""

from .common import Extractor, Message
from .. import exception


class GfycatExtractor(Extractor):
    """Base class for gfycat extractors"""
    category = "gfycat"
    filename_fmt = "{category}_{gfyName}.{extension}"
    archive_fmt = "{gfyName}"
    root = "https://gfycat.com"

    def __init__(self):
        Extractor.__init__(self)
        self.formats = (self.config("format", "mp4"), "mp4", "webm", "gif")

    def _select_format(self, gfyitem):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gfyitem:
                url = gfyitem[key]
                gfyitem["extension"] = url.rpartition(".")[2]
                return url
        return ""

    def _get_info(self, gfycat_id):
        url = "{}/cajax/get/{}".format(self.root, gfycat_id)
        data = self.request(url).json()
        if "error" in data:
            raise exception.NotFoundError("animation")
        return data["gfyItem"]


class GfycatImageExtractor(GfycatExtractor):
    """Extractor for individual images from gfycat.com"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:\w+\.)?gfycat\.com"
               r"/(?:\w+/|gifs/detail/)?([A-Za-z]+)"]
    test = [
        ("https://gfycat.com/GrayGenerousCowrie", {
            "url": "e0b5e1d7223108249b15c3c7898dd358dbfae045",
            "content": "5786028e04b155baa20b87c5f4f77453cd5edc37",
            "keyword": {
                "gfyId": "graygenerouscowrie",
                "gfyName": "GrayGenerousCowrie",
                "gfyNumber": "755075459",
                "title": "Bottom's up",
                "userName": "jackson3oh3",
                "createDate": "1495884169",
                "md5": "a4796e05b0db9ba9ce5140145cd318aa",
                "width": "400",
                "height": "224",
                "frameRate": "23",
                "numFrames": "158",
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
        ("https://gfycat.com/gifs/detail/UnequaledHastyAnkole", None),
        ("https://gfycat.com/ifr/UnequaledHastyAnkole", None),
        ("https://gfycat.com/ru/UnequaledHastyAnkole", None),
    ]

    def __init__(self, match):
        GfycatExtractor.__init__(self)
        self.gfycat_id = match.group(1)

    def items(self):
        gfyitem = self._get_info(self.gfycat_id)
        yield Message.Version, 1
        yield Message.Directory, gfyitem
        yield Message.Url, self._select_format(gfyitem), gfyitem
