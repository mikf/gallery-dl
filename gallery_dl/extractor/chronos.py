# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://chronos.to/"""

from .common import Extractor, Message
from .. import text

class ChronosExtractor(Extractor):

    category = "chronos"
    directory_fmt = ["{category}"]
    filename_fmt = "{filename}"
    pattern = [r"(?:https?://)?(?:www\.)?chronos\.to/([a-z0-9]{12})"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.token = match.group(1)

    def items(self):
        params = {
            "op": "view",
            "id": self.token,
            "pre": 1,
            "next": "Continue to image.",
        }
        page = self.request("http://chronos.to/" + self.token, method="post",
                            data=params).text
        url     , pos = text.extract(page, '<img src="', '"')
        filename, pos = text.extract(page, ' alt="', '"', pos)
        data = {
            "category": self.category,
            "token": self.token,
        }
        text.nameext_from_url(filename, data)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data
