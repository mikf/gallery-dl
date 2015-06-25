# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://manga.redhawkscans.com/"""

from .common import SequentialExtractor
from .common import Message
from .common import unescape
import os.path
import json
import re

info = {
    "category": "redhawkscans",
    "extractor": "RedHawkScansExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03} - {title}"],
    "filename": "{manga}_c{chapter:>03}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?manga\.redhawkscans\.com/reader/read/([^/]+/[^/]+/[^/]+/[^/]+).*",
    ],
}

class RedHawkScansExtractor(SequentialExtractor):

    url_base = "https://manga.redhawkscans.com/reader/read/"

    def __init__(self, match, config):
        SequentialExtractor.__init__(self, config)
        self.part = match.group(1)

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
        page = self.request(self.url_base + self.part).text
        _        , pos = self.extract(page, '<h1 class="tbtitle dnone">', '')
        manga    , pos = self.extract(page, 'title="', '"', pos)
        chapter  , pos = self.extract(page, 'title="', '"', pos)
        json_data, pos = self.extract(page, 'var pages = ', '\n', pos)
        match = re.match(r"Chapter (\d+)(?:: (.*))?", chapter)
        return {
            "category": info["category"],
            "manga": unescape(manga),
            "chapter": match.group(1),
            "language": "English",
            "title": unescape(match.group(2) or ""),
        }, json.loads(json_data[:-2])
