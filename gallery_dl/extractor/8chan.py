# -*- coding: utf-8 -*-

# Copyright 2014, 2015 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract image- and video-urls from threads on https://8ch.net/"""

from .common import SequentialExtractor, Message
from urllib.parse import unquote
import re

info = {
    "category": "8chan",
    "extractor": "InfinityChanExtractor",
    "directory": ["{category}", "{board}-{thread-id}"],
    "filename": "{timestamp}-{name}",
    "pattern": [
        r"(?:https?://)?(?:www\.)?(?:8chan\.co|8ch\.net)/([^/]+/res/\d+).*",
    ],
}

class InfinityChanExtractor(SequentialExtractor):

    url_base = "https://8ch.net"
    url_fmt = url_base + "/{board}/res/{thread-id}.html"
    regex = (
        r'>File: <a href="([^"]+)">([^<]+)\.[^<]+<.*?'
        r'<span class="postfilename"( title="([^"]+)")?>([^<]+)<'
    )

    def __init__(self, match, config):
        SequentialExtractor.__init__(self, config)
        self.match = match

    def items(self):
        yield Message.Version, 1

        metadata = self.get_job_metadata()
        yield Message.Directory, metadata

        url = self.url_fmt.format(**metadata)
        text = self.request(url).text
        for match in re.finditer(self.regex, text):
            yield Message.Url, self.get_file_url(match), self.get_file_metadata(match)

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        board, _, thread_id = self.match.group(1).split("/")
        return {
            "category": info["category"],
            "board": board,
            "thread-id": thread_id,
        }

    @staticmethod
    def get_file_metadata(match):
        """Collect metadata for a downloadable file"""
        return {
            "timestamp": match.group(2),
            "name": unquote(match.group(4) or match.group(5)),
        }

    def get_file_url(self, match):
        """Extract download-url from 'match'"""
        url = match.group(1)
        if url.startswith("/"):
            url = self.url_base + url
        return url

