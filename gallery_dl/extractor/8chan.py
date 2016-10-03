# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://8ch.net/"""

from . import chan

class InfinitychanThreadExtractor(chan.ChanThreadExtractor):
    """Extractor for images from threads from 8ch.net"""
    category = "8chan"
    pattern = [r"(?:https?://)?(?:www\.)?8ch\.net/([^/]+)/res/(\d+)"]
    test = [("https://8ch.net/tg/res/175887.html", {
        "url": "cb03fdc650ad8e796fdab553fbd5489f468d3f45",
        "keyword": "c2a7f57422558dddaf3467b9a30018e847eb4fad",
        "content": "9f51cdfee6942a18011996ca049baeb0a22f931b",
    })]
    api_url = "https://8ch.net/{board}/res/{thread}.json"
    file_url = "https://8ch.net/{board}/src/{tim}{ext}"
