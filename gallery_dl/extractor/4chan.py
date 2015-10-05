# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image- and video-urls from threads on https://www.4chan.org/"""

from .chan import ChanExtractor

info = {
    "category": "4chan",
    "extractor": "FourChanExtractor",
    "directory": ["{category}", "{board}-{thread}"],
    "filename": "{tim}-{filename}{ext}",
    "pattern": [
        r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+).*",
    ],
}

class FourChanExtractor(ChanExtractor):

    api_url = "https://a.4cdn.org/{board}/thread/{thread}.json"
    file_url = "https://i.4cdn.org/{board}/{tim}{ext}"

    def __init__(self, match):
        ChanExtractor.__init__(
            self, info["category"],
            match.group(1), match.group(2)
        )
