# -*- coding: utf-8 -*-

# Copyright 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://arch.b4k.co/"""

from . import chan


class BfourkThreadExtractor(chan.FoolfuukaThreadExtractor):
    """Extractor for images from threads on arch.b4k.co"""
    category = "b4k"
    root = "https://arch.b4k.co"
    pattern = [r"(?:https?://)?arch\.b4k\.co/([^/]+)/thread/(\d+)"]
    test = [("http://arch.b4k.co/meta/thread/196/", {
        "url": "cdd4931ac1cd00264b0b54e2e3b0d8f6ae48957e",
    })]

    def remote(self, media):
        return media["remote_media_link"]
