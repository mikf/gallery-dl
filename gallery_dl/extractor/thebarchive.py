# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://thebarchive.com/"""

from . import chan


class ThebarchiveThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on thebarchive.com"""
    category = "thebarchive"
    root = "https://thebarchive.com"
    pattern = [r"(?:https?://)?thebarchive\.com/([^/]+)/thread/(\d+)"]
    test = [("https://thebarchive.com/b/thread/739772332/", {
        "url": "e8b18001307d130d67db31740ce57c8561b5d80c",
    })]
