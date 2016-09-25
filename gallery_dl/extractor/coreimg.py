# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://coreimg.net/"""

from . import chronos

class CoreimgImageExtractor(chronos.ChronosImageExtractor):
    """Extractor for single images from coreimg.net"""
    category = "coreimg"
    pattern = [r"(?:https?://)?(?:www\.)?coreimg\.net/([a-z0-9]{12})"]
    url_base = "https://coreimg.net/"
    test = [("http://coreimg.net/ykcl5al8uzvg", {
        "url": "2b32596a2ea66b7cc784e20f3749f75f20998d78",
        "keyword": "8d71e5b820bc7177baee33ca529c91ae4521299f",
        "content": "0c8768055e4e20e7c7259608b67799171b691140",
    })]
