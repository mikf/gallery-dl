# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
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

    def __init__(self, match):
        Extractor.__init__(self)
        self.item_id = match.group(1)
        self.formats = (self.config("format", "mp4"), "mp4", "webm", "gif")

    def _select_format(self, gfycat):
        for fmt in self.formats:
            key = fmt + "Url"
            if key in gfycat:
                url = gfycat[key]
                gfycat["extension"] = url.rpartition(".")[2]
                return url

    @staticmethod
    def _clean(image):
        for key in ("dislikes", "likes", "views", "viewsNewEpoch"):
            del image[key]
        return image


class GfycatImageExtractor(GfycatExtractor):
    """Extractor for individual images from gfycat.com"""
    subcategory = "image"
    filename_fmt = "{category}_{gfyName}.{extension}"
    pattern = [r"(?:https?://)?(?:[a-z]+\.)?gfycat\.com/"
               r"(?:(?:gifs/)?detail/|ifr/)?([A-Za-z]+)"]
    test = [
        ("https://gfycat.com/GrayGenerousCowrie", {
            "url": "e0b5e1d7223108249b15c3c7898dd358dbfae045",
            "keyword": "f92a5792df3ae61817627768897f1d0dd134c2e4",
            "content": "3157cd8b3799205c5a0df98a7ee31aa85bf6491e",
        }),
        (("https://thumbs.gfycat.com/SillyLameIsabellinewheatear"
          "-size_restricted.gif"), {
            "url": "13b32e6cc169d086577d7dd3fd36ee6cdbc02726",
        }),
        ("https://gfycat.com/detail/UnequaledHastyAnkole?tagname=aww", {
            "url": "e24c9f69897fd223343782425a429c5cab6a768e",
        }),
    ]

    def items(self):
        gfycat = self._clean(self._get_info(self.item_id))
        yield Message.Version, 1
        yield Message.Directory, gfycat
        yield Message.Url, self._select_format(gfycat), gfycat

    def _get_info(self, gfycat_id):
        url = "https://gfycat.com/cajax/get/" + gfycat_id
        data = self.request(url).json()
        if "error" in data:
            raise exception.NotFoundError("animation")
        return data["gfyItem"]
