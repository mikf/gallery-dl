# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://www.turboimagehost.com"""

from .common import Extractor, Message
from .. import text

class TurboimagehostImageExtractor(Extractor):
    """Extractor for single images from turboimagehost.com"""
    category = "turboimagehost"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{index}_{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?turboimagehost\.com/p/((\d+)/[^/]+\.html)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.part, self.index = match.groups()

    def items(self):
        page = self.request("http://www.turboimagehost.com/p/" + self.part).text
        data = {
            "category": self.category,
            "index": self.index,
        }
        text.extract_all(page, (
            ('width' , 'var imWidth = ', ';'),
            ('height', 'var imHeight = ', ';'),
            ('url'   , '<a href="http://www.turboimagehost.com"><img src="', '"'),
        ), values=data)
        text.nameext_from_url(data["url"], data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, data["url"], data
