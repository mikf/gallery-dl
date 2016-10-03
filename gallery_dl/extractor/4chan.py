# -*- coding: utf-8 -*-

# Copyright 2015, 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://www.4chan.org/"""

from . import chan

class FourchanThreadExtractor(chan.ChanThreadExtractor):
    """Extractor for images from threads from 4chan.org"""
    category = "4chan"
    pattern = [r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+)"]
    test = [("https://boards.4chan.org/tg/thread/15396072/", {
        "url": "39082ad166161966d7ba8e37f2173a824eb540f0",
        "keyword": "38679a7c8054f535cba67cae13eef1ea7dbc8085",
        "content": "3081ed85a5afaeb3f430f42540e7bb5eec1908cc",
    })]
    api_url = "https://a.4cdn.org/{board}/thread/{thread}.json"
    file_url = "https://i.4cdn.org/{board}/{tim}{ext}"
