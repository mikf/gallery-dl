# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://behoimi.org/"""

from .booru import JSONBooruExtractor

info = {
    "category": "3dbooru",
    "extractor": "ThreeDeeBooruExtractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{id}_{name}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?behoimi\.org/post(?:/(?:index)?)?\?tags=([^&]+).*",
    ],
}

class ThreeDeeBooruExtractor(JSONBooruExtractor):

    def __init__(self, match):
        JSONBooruExtractor.__init__(self, match, info)
        self.api_url = "http://behoimi.org/post/index.json"
        self.headers = {
            "Referer": "http://behoimi.org/post/show/",
            "User-Agent": "Mozilla/5.0"
        }
