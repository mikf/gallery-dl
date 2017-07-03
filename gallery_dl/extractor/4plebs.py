# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.4plebs.org/"""

from . import chan


class FourplebsThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on 4plebs.org"""
    category = "4plebs"
    pattern = [r"(?:https?://)?(?:archive\.)?4plebs\.org/([^/]+)/thread/(\d+)"]
    test = [("https://archive.4plebs.org/tg/thread/54111182/", {
        "url": "85f54faf037dee29ad1c413142bcc45cd905be5a",
        "keyword": "59c414bddc58b77b3e481fbe1c4e4ea3d582b2d3",
    })]
    root = "https://archive.4plebs.org"
