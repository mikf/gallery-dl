# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://8ch.net/"""

from .chan import ChanExtractor

class InfinitychanThreadExtractor(ChanExtractor):
    """Extractor for images from threads from 8ch.net"""
    category = "8chan"
    subcategory = "thread"
    pattern = [r"(?:https?://)?(?:www\.)?8ch\.net/([^/]+)/res/(\d+)"]
    test = [("https://8ch.net/tg/res/175887.html", {
        "url": "cb03fdc650ad8e796fdab553fbd5489f468d3f45",
        "keyword": "d9388d231db6a0ea3e710a6cf46dc53dbdbb2115",
        "content": "9f51cdfee6942a18011996ca049baeb0a22f931b",
    })]
    api_url = "https://8ch.net/{board}/res/{thread}.json"
    file_url = "https://8ch.net/{board}/src/{tim}{ext}"

    def __init__(self, match):
        ChanExtractor.__init__(
            self, match.group(1), match.group(2)
        )
