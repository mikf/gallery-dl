# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Direct link handling"""

from .common import Extractor, Message
from .. import text


class DirectlinkExtractor(Extractor):
    """Extractor for direct links to images"""
    category = "directlink"
    directory_fmt = []
    filename_fmt = "{filename}"
    pattern = [r"https?://[^?&#]+\.(?:jpe?g|png|gifv?|webm|mp4)"]
    test = [("https://i.imgur.com/21yMxCS.png", {
        "url": "6f2dcfb86815bdd72808c313e5f715610bc7b9b2",
        "keyword": "6a9636d8dd6f71f14d6d20d24153fc83a9895ed9",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.string

    def items(self):
        data = text.nameext_from_url(self.url)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, self.url, data
