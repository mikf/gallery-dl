# -*- coding: utf-8 -*-

# Copyright 2017-2020 Mike Fährmann
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
    filename_fmt = "{domain}/{path}/{filename}.{extension}"
    archive_fmt = filename_fmt
    pattern = (r"(?i)https?://(?P<domain>[^/?#]+)/(?P<path>[^?#]+\."
               r"(?:jpe?g|jpe|png|gif|web[mp]|mp4|mkv|og[gmv]|opus))"
               r"(?:\?(?P<query>[^/?#]*))?(?:#(?P<fragment>.*))?$")
    test = (
        (("https://en.wikipedia.org/static/images/project-logos/enwiki.png"), {
            "url": "18c5d00077332e98e53be9fed2ee4be66154b88d",
            "keyword": "105770a3f4393618ab7b811b731b22663b5d3794",
        }),
        # empty path
        (("https://example.org/file.webm"), {
            "url": "2d807ed7059d1b532f1bb71dc24b510b80ff943f",
            "keyword": "29dad729c40fb09349f83edafa498dba1297464a",
        }),
        # more complex example
        ("https://example.org/path/to/file.webm?que=1&ry=2#fragment", {
            "url": "114b8f1415cc224b0f26488ccd4c2e7ce9136622",
            "keyword": "06014abd503e3b2b58aa286f9bdcefdd2ae336c0",
        }),
        # percent-encoded characters
        ("https://example.org/%27%3C%23/%23%3E%27.jpg?key=%3C%26%3E", {
            "url": "2627e8140727fdf743f86fe18f69f99a052c9718",
            "keyword": "831790fddda081bdddd14f96985ab02dc5b5341f",
        }),
        # upper case file extension (#296)
        ("https://post-phinf.pstatic.net/MjAxOTA1MjlfMTQ4/MDAxNTU5MTI2NjcyNTkw"
         ".JUzkGb4V6dj9DXjLclrOoqR64uDxHFUO5KDriRdKpGwg.88mCtd4iT1NHlpVKSCaUpP"
         "mZPiDgT8hmQdQ5K_gYyu0g.JPEG/2.JPG"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.data = match.groupdict()

    def items(self):
        data = self.data
        for key, value in data.items():
            if value:
                data[key] = text.unquote(value)

        data["path"], _, name = data["path"].rpartition("/")
        data["filename"], _, ext = name.rpartition(".")
        data["extension"] = ext.lower()
        data["_http_headers"] = {"Referer": self.url}

        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, self.url, data
