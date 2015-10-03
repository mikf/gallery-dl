# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract manga pages from http://manga.redhawkscans.com/"""

from .common import SequentialExtractor, Message
from .. import text
import os.path
import json
import re

info = {
    "category": "redhawkscans",
    "extractor": "RedHawkScansExtractor",
    "directory": ["{category}", "{manga}", "c{chapter:>03}{chapter-minor} - {title}"],
    "filename": "{manga}_c{chapter:>03}{chapter-minor}_{page:>03}.{extension}",
    "pattern": [
        r"(?:https?://)?manga\.redhawkscans\.com/reader/read/(.+)(?:/page)?.*",
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
        response = self.request(self.url_base + self.part)
        response.encoding = "utf-8"
        page = response.text
        _        , pos = text.extract(page, '<h1 class="tbtitle dnone">', '')
        manga    , pos = text.extract(page, 'title="', '"', pos)
        chapter  , pos = text.extract(page, '">', '</a>', pos)
        json_data, pos = text.extract(page, 'var pages = ', ';\r\n', pos)
        match = re.match(r"(Chapter (\d+)([^:+]*)(?:: (.*))?|[^:]+)", chapter)
        return {
            "category": info["category"],
            "manga": text.unescape(manga),
            "chapter": match.group(2) or match.group(1),
            "chapter-minor": match.group(3) or "",
            "language": "English",
            "title": text.unescape(match.group(4) or ""),
        }, json.loads(json_data)
