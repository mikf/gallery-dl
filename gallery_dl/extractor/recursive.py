# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Recursive extractor"""

import re
from .common import Extractor, Message
from .. import extractor, adapter, util


class RecursiveExtractor(Extractor):
    """Extractor that fetches URLs from a remote or local source"""
    category = "recursive"
    pattern = [r"r(?:ecursive)?:(.+)"]
    test = [("recursive:https://pastebin.com/raw/FLwrCYsT", {
        "url": "eee86d65c346361b818e8f4b2b307d9429f136a2",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.session.mount("file://", adapter.FileAdapter())
        self.url = match.group(1)

    def items(self):
        blist = self.config(
            "blacklist", ("directlink",) + util.SPECIAL_EXTRACTORS)
        page = self.request(self.url).text
        yield Message.Version, 1
        with extractor.blacklist(blist):
            for match in re.finditer(r"https?://[^\s\"']+", page):
                yield Message.Queue, match.group(0), {}
