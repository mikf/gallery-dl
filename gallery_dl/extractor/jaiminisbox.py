# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga-chapters from https://jaiminisbox.com/"""

from .foolslide import FoolslideChapterExtractor


class JaiminisboxChapterExtractor(FoolslideChapterExtractor):
    """Extractor for manga-chapters from jaiminisbox.com"""
    category = "jaiminisbox"
    pattern = [(r"(?:https?://)?(?:www\.)?(jaiminisbox.com/reader/read/"
                r"[^/]+/([a-z]{2})/\d+/\d+)")]
    test = [("https://jaiminisbox.com/reader/read/uratarou/en/0/1/", {
        "url": "f021de7f31ee3a3f688fdf3e8183aef4226c2b50",
        "keyword": "836e94f68b78159cc10d12b72c981c276ff45b3f",
    })]

    def __init__(self, match):
        url = "https://" + match.group(1)
        FoolslideChapterExtractor.__init__(self, url, match.group(2))
