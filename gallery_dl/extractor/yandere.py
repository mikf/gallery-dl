# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://yande.re/"""

from .booru import JSONBooruExtractor

info = {
    "category": "yandere",
    "extractor": "YandereExtractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{id}_{md5}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?yande\.re/post\?tags=([^&]+).*",
    ],
}

class YandereExtractor(JSONBooruExtractor):

    def __init__(self, match):
        JSONBooruExtractor.__init__(self, match, info)
        self.api_url = "https://yande.re/post.json"
