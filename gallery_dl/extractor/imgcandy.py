# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://imgcandy.net/"""

from .common import Extractor, Message
from .. import text

class ImgcandyImageExtractor(Extractor):
    """Extractor for single images from imgcandy.net"""
    category = "imgcandy"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    pattern = [(r"(?:https?://)?(?:www\.)?imgcandy\.net/img-([a-z0-9]+)"
                r"(?:_(.+))?\.html")]
    test = [("http://imgcandy.net/img-57d02527efee8_test-テスト.png.html", {
        "url": "bc3c9207b10dbfe8e65ccef5b9e3194a7427b4fa",
        "keyword": "1ed1587ef38a6b26ce28b35857a78417239d197a",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token, self.filename = match.groups()

    def items(self):
        params = {"imgContinue": "Continue+to+image+...+"}
        page = self.request("http://imgcandy.net/img-" + self.token + ".html",
                            method="post", data=params).text
        url = text.extract(page, "<img class='centred' src='", "'")[0]
        data = text.nameext_from_url(self.filename or url, {"token": self.token})
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
