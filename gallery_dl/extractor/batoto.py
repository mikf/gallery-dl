# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://bato.to/"""

from .common import AsynchronousExtractor, Message
from .. import text
import os.path
import re

info = {
    "category": "batoto",
    "extractor": "BatotoExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03} - {title}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?bato\.to/read/_/(\d+).*",
    ],
}

class BatotoExtractor(AsynchronousExtractor):

    url_base = "http://bato.to/read/_/"

    def __init__(self, match):
        AsynchronousExtractor.__init__(self)
        self.chapter_id = match.group(1)

    def items(self):
        yield Message.Version, 1
        url = self.url_base + self.chapter_id
        while url:
            url, data = self.get_page_metadata(url)
            yield Message.Directory, data
            yield Message.Url, data["image-url"], data

    def get_page_metadata(self, page_url):
        """Collect next url and metadata for one manga-page"""
        page = self.request(page_url).text
        _    , pos = text.extract(page, 'selected="selected"', '')
        title, pos = text.extract(page, ': ', '<', pos)
        _    , pos = text.extract(page, 'selected="selected"', '', pos)
        trans, pos = text.extract(page, '>', '<', pos)
        _    , pos = text.extract(page, '<div id="full_image"', '', pos)
        image, pos = text.extract(page, '<img src="', '"', pos)
        url  , pos = text.extract(page, '<a href="', '"', pos)
        mmatch = re.search(
            r"<title>(.+) - (?:vol (\d+) )?"
            r"ch (\d+)[^ ]+ Page (\d+) | Batoto!</title>",
            page
        )
        tmatch = re.match(
            r"(.+) - ([^ ]+)",
            trans
        )
        filename = text.unquote(text.filename_from_url(image))
        name, ext = os.path.splitext(filename)
        return url, {
            "category": info["category"],
            "chapter-id": self.chapter_id,
            "manga": text.unescape(mmatch.group(1)),
            "volume": mmatch.group(2) or "",
            "chapter": mmatch.group(3),
            "page": mmatch.group(4),
            "group": tmatch.group(1),
            "language": tmatch.group(2),
            "title": text.unescape(title),
            "image-url": image,
            "name": name,
            "extension": ext[1:],
        }
