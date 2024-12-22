# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann
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
               r"(?:jpe?g|jpe|png|gif|bmp|svg|web[mp]|avif|heic|psd"
               r"|mp4|m4v|mov|mkv|og[gmv]|wav|mp3|opus|zip|rar|7z|pdf|swf))"
               r"(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?$")
    example = "https://en.wikipedia.org/static/images/project-logos/enwiki.png"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.data = data = match.groupdict()
        self.subcategory = ".".join(data["domain"].rsplit(".", 2)[-2:])

    def items(self):
        data = self.data
        for key, value in data.items():
            if value:
                data[key] = text.unquote(value)

        data["path"], _, name = data["path"].rpartition("/")
        data["filename"], _, ext = name.rpartition(".")
        data["extension"] = ext.lower()
        data["_http_headers"] = {
            "Referer": self.url.encode("latin-1", "ignore")}

        yield Message.Directory, data
        yield Message.Url, self.url, data
