# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://boards.fireden.net/"""

from . import chan


class FiredenThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on boards.fireden.net"""
    category = "fireden"
    root = "https://boards.fireden.net"
    pattern = [r"(?:https?://)?boards\.fireden\.net/([^/]+)/thread/(\d+)"]
    test = [("https://boards.fireden.net/a/thread/159803223/", {
        "url": "01b7baacfb0656a68e566368290e3072b27f86c9",
    })]
