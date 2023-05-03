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

BASE_PATTERN = UrlshortenerExtractor.update(INSTANCES)


class UrlshortenerLinkExtractor(UrlshortenerExtractor):
    """Extractor for general-purpose URL shorteners"""
    subcategory = "link"
    pattern = BASE_PATTERN + r"/([^/?#]+)"
    test = (
        ("https://bit.ly/3cWIUgq", {
            "count": 1,
            "pattern": "^https://gumroad.com/l/storm_b1",
        }),
        ("https://t.co/bCgBY8Iv5n", {
            "count": 1,
            "pattern": "^https://twitter.com/elonmusk/status/"
                       "1421395561324896257/photo/1",
        }),
        ("https://t.co/abcdefghij", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        UrlshortenerExtractor.__init__(self, match)
        self.id = match.group(match.lastindex)

        try:
            self.headers = INSTANCES[self.category]["headers"]
        except Exception:
            self.headers = None

    def items(self):
        response = self.request(
            "{}/{}".format(self.root, self.id), headers=self.headers,
            method="HEAD", allow_redirects=False, notfound="URL")
        try:
            yield Message.Queue, response.headers["location"], {}
        except KeyError:
            raise exception.StopExtraction("Unable to resolve short URL")
