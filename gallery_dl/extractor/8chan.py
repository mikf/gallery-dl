# -*- coding: utf-8 -*-

# Copyright 2014-2016 Mike Fährmann
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
    test = [("https://8ch.net/tg/res/175887.html", {
        "url": "646d4230b40f9cff3f8674e3efe44bba3af4924b",
        "keyword": "cdb061d01e415631b79649d297dd7f995d48f8c4",
        "content": "81e21a3cc87f64f224a966f207e8e1731216c345",
    })]
    api_url = "https://8ch.net/{board}/res/{thread}.json"
    file_url = "https://media.8ch.net/{board}/src/{tim}{ext}"
    file_url_v2 = "https://media.8ch.net/file_store/{tim}{ext}"

    def build_url(self, post):
        fmt = self.file_url if len(post["tim"]) < 64 else self.file_url_v2
        return fmt.format_map(post)
