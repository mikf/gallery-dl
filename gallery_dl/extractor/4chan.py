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
    test = [("https://boards.4chan.org/tg/thread/15396072/", {
        "url": "39082ad166161966d7ba8e37f2173a824eb540f0",
        "keyword": "9b610fd3674653728516c34ec65925a024cc0074",
        "content": "3081ed85a5afaeb3f430f42540e7bb5eec1908cc",
    })]
    api_url = "https://a.4cdn.org/{board}/thread/{thread}.json"
    file_url = "https://i.4cdn.org/{board}/{tim}{ext}"

    def __init__(self, match):
        ChanExtractor.__init__(
            self, match.group(1), match.group(2)
        )
