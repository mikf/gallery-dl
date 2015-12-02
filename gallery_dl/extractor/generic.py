# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Generic extractor"""

import re
from .common import Extractor, Message

class GenericExtractor(Extractor):

    category = "generic"
    pattern = ["generic:(.+)"]

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(1)

    def items(self):
        page = self.request(self.url).text
        yield Message.Version, 1
        for match in re.finditer("https?://[^ \"']+", page):
            yield Message.Queue, match.group(0)
