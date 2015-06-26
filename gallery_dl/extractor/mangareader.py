# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://www.mangareader.net/"""

from .common import AsynchronousExtractor
from .common import Message
from .common import unescape, filename_from_url
from urllib.parse import unquote
import os.path
import re

info = {
    "category": "mangareader",
    "extractor": "MangaReaderExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?mangareader\.net(/[^/]+/\d+).*",
        r"(?:https?://)?(?:www\.)?mangareader\.net(/\d+-\d+-\d+/[^/]+/chapter-\d+.html)",
    ],
}

class MangaReaderExtractor(AsynchronousExtractor):

    url_base = "http://www.mangareader.net"

    def __init__(self, match, config):
        AsynchronousExtractor.__init__(self, config)
        self.part = match.group(1)

    def items(self):
        yield Message.Version, 1
        url = self.url_base + self.part
        while True:
            url, image_url, data = self.get_page_metadata(url)
            print(url)
            if url is None:
                return
            yield Message.Directory, data
            yield Message.Url, image_url, data

    def get_page_metadata(self, page_url):
        """Collect next url, image-url and metadata for one manga-page"""
        page = self.request(page_url).text
        descr  , pos = self.extract(page, '<meta name="description" content="', '"')
        _      , pos = self.extract(page, '<div id="imgholder">', '', pos)
        print(page[pos:pos+3])
        if page[pos+1] != "a":
            return None, None, None
        url    , pos = self.extract(page, ' href="', '"', pos)
        width  , pos = self.extract(page, '<img id="img" width="', '"', pos)
        height , pos = self.extract(page, ' height="', '"', pos)
        image  , pos = self.extract(page, ' src="', '"', pos)
        filename = unquote(filename_from_url(image))
        name, ext = os.path.splitext(filename)
        match = re.match(r"(.*) (\d+) - Read \1 \2 Manga Scans Page (\d+)", descr)
        manga, chapter, page = match.groups()

        return self.url_base + url, image, {
            "category": info["category"],
            "manga": unescape(manga),
            "chapter": chapter,
            "page": page,
            "width": width,
            "height": height,
            "language": "English",
            "name": name,
            "extension": ext[1:],
        }
