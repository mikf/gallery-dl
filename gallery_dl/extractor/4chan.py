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
        r"(?:https?://)?boards\.4chan\.org/([^/]+)/thread/(\d+).*",
    ],
}

class FourChanExtractor(SequentialExtractor):

    url_fmt = "https://boards.4chan.org/{0}/res/{1}.html"
    regex = (
        r'<a (?:title="(?P<orig_name>[^"]+)" )?href="'
        r'(?P<url>//i.4cdn.org/[^/]+/(?P<timestamp>\d+)\.(?P<extension>[^"]+))'
        r'" target="_blank">(?P<name>[^<]+)</a> '
        r'\((?P<size>[^,]+), (?P<width>\d+)x(?P<height>\d+)\)'
    )

    def __init__(self, match, config):
        SequentialExtractor.__init__(self, config)
        self.match = match
        self.metadata = None

    def items(self):
        yield Message.Version, 1

        url = self.url_fmt.format(*self.match.groups())
        text = self.request(url).text
        self.metadata = self.get_job_metadata(text)

        yield Message.Directory, self.metadata
        for match in re.finditer(self.regex, text):
            yield Message.Url, self.get_file_url(match), self.get_file_metadata(match)

    def get_job_metadata(self, text):
        """Collect metadata for extractor-job"""
        board, thread_id = self.match.groups()
        title, _ = self.extract(text, '"description" content="', ' - &quot;/')
        return {
            "category": info["category"],
            "board": board,
            "thread-id": thread_id,
            "title": unquote(title),
        }

    def get_file_metadata(self, match):
        """Collect metadata for a downloadable file"""
        data = self.metadata
        data.update(match.groupdict(default=""))
        data["name"] = unquote(data["orig_name"] or data["name"])
        return data

    @staticmethod
    def get_file_url(match):
        """Extract download-url from 'match'"""
        return "https:" + match.group("url")
