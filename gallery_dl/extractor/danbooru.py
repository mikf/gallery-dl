# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image-urls from https://danbooru.donmai.us/"""

from .booru import JSONBooruExtractor
from .. import text

class DanbooruTagExtractor(JSONBooruExtractor):
    """Extract images bsaed on search-tags"""

    info = {
        "category": "danbooru",
        "directory": ["{category}", "{tags}"],
        "filename": "{category}_{id}_{md5}.{extension}",
    }
    pattern = [
        r"(?:https?://)?(?:www\.)?danbooru.donmai.us/posts\?(?:utf8=%E2%9C%93&)?tags=([^&]+)",
    ]

    def __init__(self, match):
        JSONBooruExtractor.__init__(self)
        self.api_url = "https://danbooru.donmai.us/posts.json"
        self.tags = text.unquote(match.group(1))
        self.params = {"tags": self.tags}

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": self.info["category"],
            "tags": self.tags,
        }
