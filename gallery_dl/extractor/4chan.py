# -*- coding: utf-8 -*-

# Copyright 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image- and video-urls from threads on https://www.4chan.org/"""

from .common import SequentialExtractor, Message
from urllib.parse import unquote
import re

info = {
    "category": "4chan",
    "extractor": "FourChanExtractor",
    "directory": ["{category}", "{board}-{thread-id}"],
    "filename": "{timestamp}-{name}",
    "pattern": [
        r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+)(?:/([^#]*))?",
    ],
}

class FourChanExtractor(SequentialExtractor):

    url_fmt = "https://boards.4chan.org/{board}/res/{thread-id}.html"
    regex = (
        r'<a href="(//i.4cdn.org/[^/]+/(\d+)\.([^"]+))"'
        r' target="_blank">([^<]+)</a>'
    )

    def __init__(self, match, config):
        SequentialExtractor.__init__(self, config)
        self.metadata = self.get_job_metadata(match)

    def items(self):
        yield Message.Version, 1
        yield Message.Directory, self.metadata

        url = self.url_fmt.format(**self.metadata)
        text = self.request(url).text
        for match in re.finditer(self.regex, text):
            yield Message.Url, self.get_file_url(match), self.get_file_metadata(match)

    @staticmethod
    def get_job_metadata(match):
        """Collect metadata for extractor-job"""
        board, thread_id, title = match.groups()
        return {
            "category": info["category"],
            "board": board,
            "thread-id": thread_id,
            "title": title,
        }

    def get_file_metadata(self, match):
        """Collect metadata for a downloadable file"""
        data = self.metadata
        data["timestamp"] = match.group(2)
        data["extension"] = match.group(3)
        data["name"] = unquote(match.group(4))
        return data

    @staticmethod
    def get_file_url(match):
        """Extract download-url from 'match'"""
        return "https:" + match.group(1)
