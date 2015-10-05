# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://e621.net/"""

from .booru import JSONBooruExtractor

info = {
    "category": "e621",
    "extractor": "E621Extractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{name}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?e621\.net/post/index/\d+/([^?]+)",
        r"(?:https?://)?(?:www\.)?e621\.net/post\?tags=([^&]+).*"
    ],
}

class E621Extractor(JSONBooruExtractor):

    def __init__(self, match):
        JSONBooruExtractor.__init__(self, match, info)
        self.api_url = "https://e621.net/post/index.json"
