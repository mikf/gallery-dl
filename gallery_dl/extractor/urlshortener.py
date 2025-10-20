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
    pattern = rf"{BASE_PATTERN}(/[^/?#]+)"
    example = "https://bit.ly/abcde"

    def items(self):
        url = self.root + self.groups[-1]
        location = self.request_location(
            url, headers=self.config_instance("headers"), notfound="URL")
        if not location:
            raise exception.AbortExtraction("Unable to resolve short URL")
        yield Message.Queue, location, {}
