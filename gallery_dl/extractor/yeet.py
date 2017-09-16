# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.yeet.net/"""

from . import chan


class YeetThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on archive.yeet.net"""
    category = "yeet"
    root = "https://archive.yeet.net"
    pattern = [r"(?:https?://)?archive\.yeet\.net/([^/]+)/thread/(\d+)"]
    test = [("https://archive.yeet.net/yeet/thread/359/", {
        "url": "ced64a1aadaafc4f359ab89d9f801050731803f1",
    })]
    referer = False
