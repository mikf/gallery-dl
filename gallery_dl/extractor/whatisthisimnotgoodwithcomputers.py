# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://archive.whatisthisimnotgoodwithcomputers.com"""

from . import chan


class WitingwcThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for archive.whatisthisimnotgoodwithcomputers.com"""
    category = "whatisthisimnotgoodwithcomputers"
    root = "https://archive.whatisthisimnotgoodwithcomputers.com"
    pattern = [r"(?:https?://)?archive\.whatisthisimnotgoodwithcomputers\.com/"
               r"([^/]+)/thread/(\d+)"]
    test = [(("https://archive.whatisthisimnotgoodwithcomputers.com/"
              "ref/thread/1094/"), {
        "url": "cf8f6d4b4950767d2131de308ebc96eec05b04f6",
    })]
