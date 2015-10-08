# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://powermanga.org/"""

from .common import Extractor, Message
from .. import text
import os.path
import json

info = {
    "category": "powermanga",
    "extractor": "PowerMangaExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03} - {title}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?(read(?:er)?\.powermanga\.org/read/[^/]+/([^/]+)/\d+/(\d+))/.*",
    ],
}

class PowerMangaExtractor(Extractor):

    def __init__(self, match):
        Extractor.__init__(self)
        self.url = match.group(1)
        self.language = match.group(2)
        self.chapter = match.group(3)

    def items(self):
        yield Message.Version, 1
        data, pages = self.get_job_metadata()
        yield Message.Directory, data
        for page_index, page_data in enumerate(pages, 1):
            name, ext = os.path.splitext(page_data["filename"])
            page_data.update(data)
            page_data["page"] = page_index
            page_data["name"] = name
            page_data["extension"] = ext[1:]
            yield Message.Url, "https" + page_data["url"][4:], page_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        url = "https://" + self.url + "/page/1"
        page = self.request(url).text
        manga, pos = text.extract(page, '<title>', ' :: ')
        _    , pos = text.extract(page, '<h1 class="tbtitle dnone">', '', pos)
        title, pos = text.extract(page, 'title="Chapter {}: '
                                  .format(self.chapter), '"', pos)
        json_data, _ = text.extract(page, 'var pages = ', ';\n', pos)
        return {
            "category": info["category"],
            "manga": text.unescape(manga),
            "chapter": self.chapter,
            "lang": self.language,
            "language": "English", #TODO: lookup table for language codes (en, it, ch, ...)
            "title": text.unescape(title),
        }, json.loads(json_data)
