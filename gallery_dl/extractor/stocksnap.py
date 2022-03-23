# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://stocksnap.io/"""

from .common import Extractor, Message
from .. import text, util

BASE_PATTERN = r"(?:https?://)?stocksnap\.io"


class StocksnapExtractor(Extractor):
    """Base class for stocksnap extractors"""
    category = "stocksnap"
    directory_fmt = ("{category}", "{keywords[0]}")
    filename_fmt = "{img_id}.{extension}"
    archive_fmt = "{id}"
    root = "https://stocksnap.io"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)


class StocksnapSearchExtractor(StocksnapExtractor):
    """Extractor for stocksnap search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/([^/?#]+)(?:\?([^/?#]+))?"
    directory_fmt = ("{category}", "{subcategory}", "{search}")
    test = ("https://stocksnap.io/search/man face/", {
        "pattern": r"https://cdn\.stocksnap\.com/",
        "range": "1-30",
        "count": 30,
    })

    def __init__(self, match):
        StocksnapExtractor.__init__(self, match)
        self.search = match.group(1)
        self.query = match.group(2)

    def metadata(self):
        return {"search": self.search}

    def _pagination(self, url_fmt, params: dict = None, results=False):
        page = 1
        while page:
            try:
                r = self.request(url_fmt % (page) , params=params)
                photos = r.json()
            except Exception as e:
                print(e)
                return
            page = photos.get("nextPage", 0)
            if results:
                photos = photos["results"]
            yield from photos

    def photos(self):
        url_fmt = self.root + "/api/search-photos/" + \
            text.unquote(self.item) + "/relevance/desc/%s/"
        params = {}
        if self.query:
            params.update(text.parse_query(self.query))
        return self._pagination(url_fmt, params, True)

    def items(self):
        data = self.metadata()
        for photo in self.photos():
            util.delete_items(
                photo, ("description", "nsfw", "tagLinks", "likeHref"))
            filename = "%s-%s_%s.jpg" % (photo["keywords"][0],
                                         photo["keywords"][1], photo["img_id"])
            url = "https://cdn.stocksnap.io/img-thumbs/960w/" + filename
            text.nameext_from_url(url, photo)

            photo["extension"] = "jpg"
            photo["filename"] = filename
            photo.update(data)

            yield Message.Directory, photo
            yield Message.Url, url, photo
