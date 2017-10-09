# -*- coding: utf-8 -*-

# Copyright 2014-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and videos from https://8ch.net/"""

from . import chan


class InfinitychanThreadExtractor(chan.ChanThreadExtractor):
    """Extractor for images from threads from 8ch.net"""
    category = "8chan"
    filename_fmt = "{time}-{filename}{ext}"
    pattern = [r"(?:https?://)?(?:www\.)?8ch\.net/([^/]+)/res/(\d+)"]
    test = [("https://8ch.net/wh40k/res/1.html", {
        "url": "9220c79950d3f9cdd2c0436e816aec6b8342fac1",
        "keyword": "df5773339c5864c71b63fc26ca60ea7098b83cb1",
    })]
    api_url = "https://8ch.net/{board}/res/{thread}.json"
    file_url = "https://media.8ch.net/{board}/src/{tim}{ext}"
    file_url_v2 = "https://media.8ch.net/file_store/{tim}{ext}"

    def build_url(self, post):
        fmt = self.file_url if len(post["tim"]) < 64 else self.file_url_v2
        return fmt.format_map(post)
