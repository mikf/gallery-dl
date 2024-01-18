# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for general-purpose URL shorteners"""

from .common import BaseExtractor, Message
from .. import exception


class UrlshortenerExtractor(BaseExtractor):
    """Base class for URL shortener extractors"""
    basecategory = "urlshortener"


BASE_PATTERN = UrlshortenerExtractor.update({
    "bitly": {
        "root": "https://bit.ly",
        "pattern": r"bit\.ly",
    },
    "tco": {
        # t.co sends 'http-equiv="refresh"' (200) when using browser UA
        "headers": {"User-Agent": None},
        "root": "https://t.co",
        "pattern": r"t\.co",
    },
})


class UrlshortenerLinkExtractor(UrlshortenerExtractor):
    """Extractor for general-purpose URL shorteners"""
    subcategory = "link"
    pattern = BASE_PATTERN + r"/([^/?#]+)"
    example = "https://bit.ly/abcde"

    def __init__(self, match):
        UrlshortenerExtractor.__init__(self, match)
        self.id = match.group(match.lastindex)

    def _init(self):
        self.headers = self.config_instance("headers")

    def items(self):
        response = self.request(
            "{}/{}".format(self.root, self.id), headers=self.headers,
            method="HEAD", allow_redirects=False, notfound="URL")
        try:
            yield Message.Queue, response.headers["location"], {}
        except KeyError:
            raise exception.StopExtraction("Unable to resolve short URL")
