# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://desuarchive.org/"""

from . import chan


class DesuarchiveThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on desuarchive.org"""
    category = "desuarchive"
    root = "https://desuarchive.org"
    pattern = [r"(?:https?://)?desuarchive\.org/([^/]+)/thread/(\d+)"]
    test = [("https://desuarchive.org/a/thread/159542679/", {
        "url": "e7d624aded15a069194e38dc731ec23217a422fb",
    })]
