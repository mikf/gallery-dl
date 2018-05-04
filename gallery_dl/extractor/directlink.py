# -*- coding: utf-8 -*-

# Copyright 2017-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Direct link handling"""

from .common import Extractor, Message
from .. import text


class DirectlinkExtractor(Extractor):
    """Extractor for direct links to images and other media files"""
    category = "directlink"
    filename_fmt = "{domain}/{path}"
    archive_fmt = "{domain}/{path}"
    pattern = [r"https?://(?P<domain>[^/]+)/(?P<path>[^?&#]+\."
               r"(?:jpe?g|jpe|png|gif|web[mp]|mp4|mkv|og[gmv]|opus))"
               r"(?:\?(?P<query>[^/?#]*))?(?:#(?P<fragment>.*))?$"]
    test = [
        (("https://en.wikipedia.org/static/images/project-logos/enwiki.png"), {
            "url": "18c5d00077332e98e53be9fed2ee4be66154b88d",
            "keyword": "66bce3a0a6872d8497e1984eb49d54a3ed0d3d5e",
        }),
        # more complex example
        ("https://example.org/path/file.webm?que=1&ry=2#fragment", {
            "url": "fd4aec8a32842343394e6078a06c3e6b647bf671",
            "keyword": "ed008f35fc18dddb2f448a18d160c949bb3b054c",
        }),
        # percent-encoded characters
        ("https://example.org/%27%3C%23/%23%3E%27.jpg?key=%3C%26%3E", {
            "url": "2627e8140727fdf743f86fe18f69f99a052c9718",
            "keyword": "c658b8b6213e46be15a25e492df385ece5771bdf",
        }),
    ]

    def __init__(self, match):
        Extractor.__init__(self)
        self.data = match.groupdict()
        self.url = match.string

    def items(self):
        text.nameext_from_url(self.url, self.data)
        for key, value in self.data.items():
            if value:
                self.data[key] = text.unquote(value)

        yield Message.Version, 1
        yield Message.Directory, self.data
        yield Message.Url, self.url, self.data
