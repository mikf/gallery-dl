# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fapachi.com/"""

from .common import Extractor, Message
from .. import text


class FapachiPostExtractor(Extractor):
    """Extractor for individual posts on fapachi.com"""
    category = "fapachi"
    subcategory = "post"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = "{user}_{id}.{extension}"
    archive_fmt = "{user}_{id}"
    pattern = (r"(?:https?://)?(?:www\.)?fapachi\.com"
               r"/(?!search/)([^/?#]+)/media/(\d+)")
    root = "https://fapachi.com"
    test = (
        # NSFW
        ("https://fapachi.com/sonson/media/0082", {
            "pattern": (r"https://fapachi\.com/models/s/o/"
                        r"sonson/1/full/sonson_0082\.jpeg"),
            "keyword": {
                "user": "sonson",
                "id"  : "0082",
            },
        }),
        # NSFW
        ("https://fapachi.com/ferxiita/media/0159"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user, self.id = match.groups()

    def items(self):
        data = {
            "user": self.user,
            "id"  : self.id,
        }
        page = self.request("{}/{}/media/{}".format(
            self.root, self.user, self.id)).text
        url = self.root + text.extr(page, 'd-block" src="', '"')
        yield Message.Directory, data
        yield Message.Url, url, text.nameext_from_url(url, data)


class FapachiUserExtractor(Extractor):
    """Extractor for all posts from a fapachi user"""
    category = "fapachi"
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.)?fapachi\.com"
               r"/(?!search(?:/|$))([^/?#]+)(?:/page/(\d+))?$")
    root = "https://fapachi.com"
    test = (
        ("https://fapachi.com/sonson", {
            "pattern": FapachiPostExtractor.pattern,
            "range"  : "1-50",
            "count"  : 50,
        }),
        ("https://fapachi.com/ferxiita/page/3"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)
        self.num = text.parse_int(match.group(2), 1)

    def items(self):
        data = {"_extractor": FapachiPostExtractor}
        while True:
            page = self.request("{}/{}/page/{}".format(
                self.root, self.user, self.num)).text
            for post in text.extract_iter(page, 'model-media-prew">', ">"):
                url = self.root + text.extr(post, '<a href="', '"')
                yield Message.Queue, url, data

            if '">Next page</a>' not in page:
                return
            self.num += 1
