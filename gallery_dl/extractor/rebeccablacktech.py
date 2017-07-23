# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://rbt.asia/"""

from . import chan


class RebeccablacktechThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on rbt.asia"""
    category = "rbt"
    root = "https://rbt.asia"
    pattern = [r"(?:https?://)?(?:(?:archive\.)?rebeccablacktech\.com"
               r"|rbt\.asia)/([^/]+)/thread/(\d+)"]
    test = [
        ("https://rbt.asia/g/thread/61487650/", {
            "url": "484f20ea9b9b58f6abb0cd37eaeab22431ac22c2",
        }),
        ("https://archive.rebeccablacktech.com/g/thread/61487650/", {
            "url": "484f20ea9b9b58f6abb0cd37eaeab22431ac22c2",
        }),
    ]
