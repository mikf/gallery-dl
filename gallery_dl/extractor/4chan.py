# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://www.4chan.org/"""

from .chan import ChanExtractor

class FourchanThreadExtractor(ChanExtractor):
    """Extractor for images from threads from 4chan.org"""
    category = "4chan"
    subcategory = "thread"
    pattern = [r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+)"]
    api_url = "https://a.4cdn.org/{board}/thread/{thread}.json"
    file_url = "https://i.4cdn.org/{board}/{tim}{ext}"

    def __init__(self, match):
        ChanExtractor.__init__(
            self, match.group(1), match.group(2)
        )
