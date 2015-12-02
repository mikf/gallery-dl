# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://imagetwist.com/"""

from .common import Extractor, Message
from .. import text

class ImagetwistExtractor(Extractor):

    category = "imagetwist"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{index}_{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?imagetwist\.com/([^/]+)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        yield Message.Version, 1
        page = self.request("http://imagetwist.com/" + self.token).text
        url     , pos = text.extract(page, '<img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        index   , pos = text.extract(url , '/', '/', 29)
        data = {
            "category": self.category,
            "token": self.token,
            "index": index,
        }
        text.nameext_from_url(filename, data)
        yield Message.Directory, data
        yield Message.Url, url, data
