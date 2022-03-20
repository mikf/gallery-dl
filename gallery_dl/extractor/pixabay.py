# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pixabay.com/photos"""

from .common import Extractor, Message
from .. import text, util
import re

BASE_PATTERN = r"(?:https?://)?pixabay\.com"


class PixabayExtractor(Extractor):
    """Base class for pixabay extractors"""
    category = "pixabay"
    directory_fmt = ("{category}", "{tags[0]}")
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"
    root = "https://pixabay.com"
    page_start = 1

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def items(self):
        fmt = self.config("format") or "2x"
        for photo in self.photos():
            util.delete_items(
                photo, ("description", "nsfw", "tagLinks", "likeHref"))
            url = photo["sources"][fmt]
            text.nameext_from_url(url, photo)

            photo["item"] = self.item
            if "alt" in photo:
                photo["tags"] = [s.lower() for s in re.findall(r"\w+", photo["alt"])]

            yield Message.Directory, photo
            yield Message.Url, url, photo


class PixabaySearchExtractor(PixabayExtractor):
    """Extractor for pixabay search results"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/photos/search/([^/?#]+)/(?:\?([^/?#]+))?"
    directory_fmt = ("{category}", "{item}")
    test = ("https://pixabay.com/photos/search/man face/", {
        "pattern": r"https://cdn\.pixabay\.com/photo/\d{4}/\d{2}/\d{2}/\d{2}/\d{2}/"
                   r"\w+-\d+_\d+\.\w+",
        "range": "1-30",
        "count": 30,
    })

    def __init__(self, match):
        PixabayExtractor.__init__(self, match)
        self.query = match.group(2)
    
    def _pagination(self, page_url, params: dict=None, results=False):
        self.page_start = params.get("pagi", 1)
        params["pagi"] = int(self.page_start)
        while True:
            json_path = self._json_path(page_url, params)
            try:
              r = self.request(self.root + json_path, params=params)
              photos = r.json()
            except Exception as e:  # sometimes the json is a 404
                print(e)
                continue
            self.total_pages = photos["page"]["totalPages"]
            if results:
                photos = photos["page"]["results"]
            yield from photos
            params["pagi"] += 1
            if params["pagi"] >= self.total_pages:
                return

    def _json_path(self, url, params: dict=None):
        html = self.request(url, params=params).text
        pat = re.compile(r"__BOOTSTRAP_URL__ = '(.*?)'")
        return pat.search(html).group(1)

    def photos(self):
        page_url = self.root + "/photos/search/" + text.unquote(self.item) + "/"
        params = {}
        if self.query:
            params.update(text.parse_query(self.query))
        return self._pagination(page_url, params, True)