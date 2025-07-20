# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://leakgallery.com"""

import re
from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?leakgallery\.com"


class LeakGalleryPostExtractor(Extractor):
    """Extractor for individual posts on leakgallery.com"""
    category = "leakgallery"
    subcategory = "post"
    pattern = BASE_PATTERN + r"/([^/?#]+)/(\d+)"
    example = "https://leakgallery.com/model/id"
    directory_fmt = ("{category}", "{creator}")
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.creator, self.id = match.groups()
        self.url = f"https://leakgallery.com/{self.creator}/{self.id}"

    def items(self):
        page = self.request(self.url).text
        video_urls = re.findall(
            r'https://cdn\.leakgallery\.com/content\d+/compressed_watermark_[^"]+\.mp4', page)
        image_urls = re.findall(
            r'https://cdn\.leakgallery\.com/content\d+/watermark_[^"]+\.jpe?g', page)

        for url in set(video_urls + image_urls):
            data = {
                "creator": self.creator,
                "id": self.id,
                "url": url,
            }
            text.nameext_from_url(url, data)
            if "extension" not in data or not data["extension"]:
                data["extension"] = url.split(".")[-1]
            yield Message.Directory, data
            yield Message.Url, url, data


class LeakGalleryUserExtractor(Extractor):
    """Extractor for all posts from a leakgallery user"""
    category = "leakgallery"
    subcategory = "user"
    pattern = BASE_PATTERN + r"/([^/?#]+)(?:/(Photos|Videos))?(?:/(MostRecent|MostViewed|MostLiked))?/?$"
    example = "https://leakgallery.com/model/Photos/MostViewed"
    directory_fmt = ("{category}", "{creator}")
    filename_fmt = "{id}_{filename}.{extension}"
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.creator = match.group(1)
        type_map = {
            None: "All",
            "Photos": "Photos",
            "Videos": "Videos"
        }
        sort_map = {
            None: "MostRecent",
            "MostRecent": "MostRecent",
            "MostViewed": "MostViewed",
            "MostLiked": "MostLiked"
        }
        self.type = type_map.get(match.group(2))
        self.sort = sort_map.get(match.group(3))

    def items(self):
        base = f"https://api.leakgallery.com/profile/{self.creator}/"
        params = {
            "type": self.type,
            "sort": self.sort
        }

        page = 1
        while True:
            response = self.request(base + str(page), params=params).json()
            medias = response.get("medias")
            if not isinstance(medias, list) or not medias:
                return

            for media in medias:
                cdn_url = "https://cdn.leakgallery.com/" + media["file_path"]
                data = {
                    "id": media["id"],
                    "creator": self.creator,
                    "category": self.category,
                    "url": cdn_url,
                    "_extractor": self,
                }
                text.nameext_from_url(cdn_url, data)
                yield Message.Directory, data
                yield Message.Url, cdn_url, data
            page += 1
