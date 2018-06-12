# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://www.4chan.org/"""

from . import chan
from .. import text


class FourchanThreadExtractor(chan.ChanThreadExtractor):
    """Extractor for images from threads from 4chan.org"""
    category = "4chan"
    pattern = [r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+)"]
    test = [("https://boards.4chan.org/tg/thread/15396072/", {
        "url": "39082ad166161966d7ba8e37f2173a824eb540f0",
        "keyword": "7ae2f4049adf0d2f835eb91b6b26b7f4ec882e0a",
        "content": "20b7b51afa51c9c31a0020a0737b889532c8d7ec",
    })]
    api_url = "https://a.4cdn.org/{board}/thread/{thread}.json"
    file_url = "https://i.4cdn.org/{board}/{tim}{ext}"

    def update(self, post, data=None):
        chan.ChanThreadExtractor.update(self, post, data)
        post["filename"] = text.unescape(post["filename"])
