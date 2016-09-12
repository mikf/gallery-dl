# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://imagetwist.com/"""

from .common import Extractor, Message
from .. import text

class ImagetwistImageExtractor(Extractor):
    """Extractor for single images from imagetwist.com"""
    category = "imagetwist"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{user}_{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imagetwist\.com/([a-z0-9]{12})"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        page = self.request("http://imagetwist.com/" + self.token).text
        url     , pos = text.extract(page, '<img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        userid  , pos = text.extract(url , '/', '/', 29)
        data = {
            "category": self.category,
            "token": self.token,
            "user": userid,
        }
        text.nameext_from_url(filename, data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
