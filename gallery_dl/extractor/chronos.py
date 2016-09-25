# -*- coding: utf-8 -*-

# Copyright 2015,2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://chronos.to/"""

from .common import Extractor, Message
from .. import text

class ChronosImageExtractor(Extractor):
    """Extractor for single images from chronos.to"""
    category = "chronos"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?chronos\.to/([a-z0-9]{12})"]
    url_base = "http://chronos.to/"
    test = [("http://chronos.to/bdrmq7rw7v4y", {
        "url": "7fcb3fe315c94283644d25ef47a644c2dc8da944",
        "keyword": "04dbc71a1154728d01c931308184050d61c5da55",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        params = {
            "op": "view",
            "id": self.token,
            "pre": 1,
            "next": "Continue+to+image.",
        }
        page = self.request(self.url_base + self.token, method="post",
                            data=params).text
        url     , pos = text.extract(page, '<br><img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        data = text.nameext_from_url(filename, {"token": self.token})
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
