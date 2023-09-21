# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comicvine.gamespot.com/"""

from .booru import BooruExtractor
from .. import text
import operator


class ComicvineTagExtractor(BooruExtractor):
    """Extractor for a gallery on comicvine.gamespot.com"""
    category = "comicvine"
    subcategory = "tag"
    basecategory = ""
    root = "https://comicvine.gamespot.com"
    per_page = 1000
    directory_fmt = ("{category}", "{tag}")
    filename_fmt = "{filename}.{extension}"
    archive_fmt = "{id}"
    pattern = (r"(?:https?://)?comicvine\.gamespot\.com"
               r"(/([^/?#]+)/(\d+-\d+)/images/.*)")
    example = "https://comicvine.gamespot.com/TAG/123-45/images/"

    def __init__(self, match):
        BooruExtractor.__init__(self, match)
        self.path, self.object_name, self.object_id = match.groups()

    def metadata(self):
        return {"tag": text.unquote(self.object_name)}

    def posts(self):
        url = self.root + "/js/image-data.json"
        params = {
            "images": text.extract(
                self.request(self.root + self.path).text,
                'data-gallery-id="', '"')[0],
            "start" : self.page_start,
            "count" : self.per_page,
            "object": self.object_id,
        }

        while True:
            images = self.request(url, params=params).json()["images"]
            yield from images

            if len(images) < self.per_page:
                return
            params["start"] += self.per_page

    def skip(self, num):
        self.page_start = num
        return num

    _file_url = operator.itemgetter("original")

    @staticmethod
    def _prepare(post):
        post["date"] = text.parse_datetime(
            post["dateCreated"], "%a, %b %d %Y")
        post["tags"] = [tag["name"] for tag in post["tags"] if tag["name"]]
