# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://danbooru.donmai.us/"""

from .booru import JSONBooruExtractor

info = {
    "category": "danbooru",
    "extractor": "DanbooruExtractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{name}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts\?(?:utf8=%E2%9C%93&)?tags=([^&]+).*",
    ],
}

class DanbooruExtractor(JSONBooruExtractor):

    def __init__(self, match, config):
        JSONBooruExtractor.__init__(self, match, config, info)
        self.api_url  = "https://danbooru.donmai.us/posts.json"
