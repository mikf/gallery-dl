# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://img.yt/"""

from .common import Extractor, Message
from .. import text
from os.path import splitext

class ImgytImageExtractor(Extractor):
    """Extractor for single images from img.yt"""
    category = "imgyt"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?img\.yt/img-([a-z0-9]+)\.html"]
    test = [("http://img.yt/img-57a2050547b97.html", {
        "url": "6801fac1ff8335bd27a1665ad27ad64cace2cd84",
        "keyword": "a20aa2215a4a6d5f4605d6370a8d605b525fc4bc",
        "content": "54592f2635674c25677c6872db3709d343cdf92f",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        data = {"category": self.category, "token": self.token}
        params = {"imgContinue": "Continue+to+image+...+"}
        page = self.request("https://img.yt/img-" + self.token + ".html",
                            method="post", data=params).text
        url     , pos = text.extract(page, "<img class='centred' src='", "'")
        filename, pos = text.extract(page, " alt='", "'", pos)
        text.nameext_from_url(filename + splitext(url)[1], data)
        if url.startswith("http:"):
            url = "https:" + url[5:]
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
