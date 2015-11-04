# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image- and video-urls from threads on https://8ch.net/"""

from .chan import ChanExtractor

info = {
    "category": "8chan",
    "extractor": "InfinityChanExtractor",
    "directory": ["{category}", "{board}-{thread}"],
    "filename": "{tim}-{filename}{ext}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?8ch\.net/([^/]+)/res/(\d+).*",
    ],
}

class InfinityChanExtractor(ChanExtractor):

    api_url = "https://8ch.net/{board}/res/{thread}.json"
    file_url = "https://8ch.net/{board}/src/{tim}{ext}"

    def __init__(self, match):
        ChanExtractor.__init__(
            self, info["category"],
            match.group(1), match.group(2)
        )
