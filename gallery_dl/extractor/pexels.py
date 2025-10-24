# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pexels.com/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pexels\.com"


class PexelsExtractor(Extractor):
    """Base class for pexels extractors"""
    category = "pexels"
    root = "https://www.pexels.com"
    archive_fmt = "{id}"
    request_interval = (1.0, 2.0)
    request_interval_min = 0.5

    def _init(self):
        self.api = self.utils().PexelsAPI(self)

    def items(self):
        for post in self.posts():
            if "attributes" in post:
                attr = post
                post = post["attributes"]
                post["type"] = attr["type"]

            post["date"] = self.parse_datetime_iso(post["created_at"][:-5])

            if "image" in post:
                url, _, query = post["image"]["download_link"].partition("?")
                name = text.extr(query, "&dl=", "&")
            elif "video" in post:
                video = post["video"]
                name = video["src"]
                url = video["download_link"]
            else:
                self.log.warning("%s: Unsupported post type", post.get("id"))
                continue

            yield Message.Directory, post
            yield Message.Url, url, text.nameext_from_url(name, post)


class PexelsCollectionExtractor(PexelsExtractor):
    """Extractor for a pexels.com collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "Collections", "{collection}")
    pattern = rf"{BASE_PATTERN}/collections/((?:[^/?#]*-)?(\w+))"
    example = "https://www.pexels.com/collections/SLUG-a1b2c3/"

    def posts(self):
        cname, cid = self.groups
        self.kwdict["collection"] = cname
        self.kwdict["collection_id"] = cid
        return self.api.collections_media(cid)


class PexelsSearchExtractor(PexelsExtractor):
    """Extractor for pexels.com search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Searches", "{search_tags}")
    pattern = rf"{BASE_PATTERN}/search/([^/?#]+)"
    example = "https://www.pexels.com/search/QUERY/"

    def posts(self):
        tag = self.groups[0]
        self.kwdict["search_tags"] = tag
        return self.api.search_photos(tag)


class PexelsUserExtractor(PexelsExtractor):
    """Extractor for pexels.com user galleries"""
    subcategory = "user"
    directory_fmt = ("{category}", "@{user[slug]}")
    pattern = rf"{BASE_PATTERN}/(@(?:(?:[^/?#]*-)?(\d+)|[^/?#]+))"
    example = "https://www.pexels.com/@USER-12345/"

    def posts(self):
        return self.api.users_media_recent(self.groups[1] or self.groups[0])


class PexelsImageExtractor(PexelsExtractor):
    subcategory = "image"
    pattern = rf"{BASE_PATTERN}/photo/((?:[^/?#]*-)?\d+)"
    example = "https://www.pexels.com/photo/SLUG-12345/"

    def posts(self):
        url = f"{self.root}/photo/{self.groups[0]}/"
        page = self.request(url).text
        return (self._extract_nextdata(page)["props"]["pageProps"]["medium"],)
