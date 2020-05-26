# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://redgifs.com/"""

from .gfycat import GfycatImageExtractor


class RedgifsImageExtractor(GfycatImageExtractor):
    """Extractor for individual images from redgifs.com"""
    category = "redgifs"
    pattern = r"(?:https?://)?redgifs\.com/watch/([A-Za-z]+)"
    test = ("https://redgifs.com/watch/foolishforkedabyssiniancat", {
        "pattern": "https://giant.gfycat.com/FoolishForkedAbyssiniancat.mp4",
        "content": "f6e03f1df9a2ff2a74092f53ee7580d2fb943533",
    })
