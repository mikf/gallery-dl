# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.nyafuu.org/"""

from . import chan


class NyafuuThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on nyafuu.org"""
    category = "nyafuu"
    root = "https://archive.nyafuu.org"
    pattern = [r"(?:https?://)?(?:archive\.)?nyafuu\.org/([^/]+)/thread/(\d+)"]
    test = [("http://archive.nyafuu.org/c/thread/2849220/", {
        "url": "bbe6f82944a45e359f5c8daf53f565913dc13e4f",
    })]
