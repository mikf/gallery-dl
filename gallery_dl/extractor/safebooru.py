# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from http://safebooru.org/"""

from .booru import XMLBooruExtractor

info = {
    "category": "safebooru",
    "extractor": "SafebooruExtractor",
    "directory": ["{category}", "{tags}"],
    "filename": "{category}_{id}_{md5}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?safebooru\.org/(?:index\.php)?\?page=post&s=list&tags=([^&]+).*",
    ],
}

class SafebooruExtractor(XMLBooruExtractor):

    def __init__(self, match):
        XMLBooruExtractor.__init__(self, match, info)
        self.api_url = "http://safebooru.org/index.php"
        self.params = {"page":"dapi", "s":"post", "q":"index", "tags":self.tags}

    def update_page(self, reset=False):
        if reset is False:
            self.params["pid"] += 1
        else:
            self.params["pid"] = 0
