# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractor for general-purpose URL shorteners"""

from .common import BaseExtractor, Message
from .. import exception


class UrlshortenerExtractor(BaseExtractor):
    """Base class for general-purpose URL shorteners"""
    basecategory = "urlshortener"
    test = (
        ("https://bit.ly/3cWIUgq", {
            "count": 1,
            "pattern": "^https://gumroad.com/l/storm_b1"
        }),
        ("https://t.co/bCgBY8Iv5n", {
            "count": 1,
            "pattern": ("^https://twitter.com/elonmusk/status/"
                        "1421395561324896257/photo/1")
        }),
    )

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.headers = INSTANCES[self.category].get("headers")
        self.url = match.group()

    def request(self, url, **kwargs):
        kwargs["headers"] = self.headers
        return BaseExtractor.request(self, url, **kwargs)

    def items(self):
        response = self.request(
            self.url, method="HEAD", allow_redirects=False, notfound="URL")
        if "location" not in response.headers:
            raise exception.StopExtraction("Unable to resolve short URL")
        yield Message.Queue, response.headers["location"], {}


INSTANCES = {
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
}

UrlshortenerExtractor.pattern = \
    UrlshortenerExtractor.update(INSTANCES) + r"/[^/?#&]+"
