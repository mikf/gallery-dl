# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://pexels.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?pexels\.com"


class PexelsExtractor(Extractor):
    """Base class for pexels extractors"""
    category = "pexels"
    root = "https://www.pexels.com"
    archive_fmt = "{id}"
    request_interval = (1.0, 2.0)
    request_interval_min = 0.5

    def _init(self):
        self.api = PexelsAPI(self)

    def items(self):
        metadata = self.metadata()

        for post in self.posts():
            if "attributes" in post:
                attr = post
                post = post["attributes"]
                post["type"] = attr["type"]

            post.update(metadata)
            post["date"] = text.parse_datetime(
                post["created_at"][:-5], "%Y-%m-%dT%H:%M:%S")

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

    def posts(self):
        return ()

    def metadata(self):
        return {}


class PexelsCollectionExtractor(PexelsExtractor):
    """Extractor for a pexels.com collection"""
    subcategory = "collection"
    directory_fmt = ("{category}", "Collections", "{collection}")
    pattern = BASE_PATTERN + r"/collections/((?:[^/?#]*-)?(\w+))"
    example = "https://www.pexels.com/collections/SLUG-a1b2c3/"

    def metadata(self):
        cname, cid = self.groups
        return {"collection": cname, "collection_id": cid}

    def posts(self):
        return self.api.collections_media(self.groups[1])


class PexelsSearchExtractor(PexelsExtractor):
    """Extractor for pexels.com search results"""
    subcategory = "search"
    directory_fmt = ("{category}", "Searches", "{search_tags}")
    pattern = BASE_PATTERN + r"/search/([^/?#]+)"
    example = "https://www.pexels.com/search/QUERY/"

    def metadata(self):
        return {"search_tags": self.groups[0]}

    def posts(self):
        return self.api.search_photos(self.groups[0])


class PexelsUserExtractor(PexelsExtractor):
    """Extractor for pexels.com user galleries"""
    subcategory = "user"
    directory_fmt = ("{category}", "@{user[slug]}")
    pattern = BASE_PATTERN + r"/(@(?:(?:[^/?#]*-)?(\d+)|[^/?#]+))"
    example = "https://www.pexels.com/@USER-12345/"

    def posts(self):
        return self.api.users_media_recent(self.groups[1] or self.groups[0])


class PexelsImageExtractor(PexelsExtractor):
    subcategory = "image"
    pattern = BASE_PATTERN + r"/photo/((?:[^/?#]*-)?\d+)"
    example = "https://www.pexels.com/photo/SLUG-12345/"

    def posts(self):
        url = "{}/photo/{}/".format(self.root, self.groups[0])
        page = self.request(url).text
        return (self._extract_nextdata(page)["props"]["pageProps"]["medium"],)


class PexelsAPI():
    """Interface for the Pexels Web API"""

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = "https://www.pexels.com/en-us/api"
        self.headers = {
            "Accept"        : "*/*",
            "Content-Type"  : "application/json",
            "secret-key"    : "H2jk9uKnhRmL6WPwh89zBezWvr",
            "Authorization" : "",
            "X-Forwarded-CF-Connecting-IP" : "",
            "X-Forwarded-HTTP_CF_IPCOUNTRY": "",
            "X-Forwarded-CF-IPRegionCode"  : "",
            "X-Client-Type" : "react",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority"      : "u=4",
        }

    def collections_media(self, collection_id):
        endpoint = "/v3/collections/{}/media".format(collection_id)
        params = {
            "page"    : "1",
            "per_page": "24",
        }
        return self._pagination(endpoint, params)

    def search_photos(self, query):
        endpoint = "/v3/search/photos"
        params = {
            "query"      : query,
            "page"       : "1",
            "per_page"   : "24",
            "orientation": "all",
            "size"       : "all",
            "color"      : "all",
            "sort"       : "popular",
        }
        return self._pagination(endpoint, params)

    def users_media_recent(self, user_id):
        endpoint = "/v3/users/{}/media/recent".format(user_id)
        params = {
            "page"    : "1",
            "per_page": "24",
        }
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 300:
                return response.json()

            elif response.status_code == 429:
                self.extractor.wait(seconds=600)

            else:
                self.extractor.log.debug(response.text)
                raise exception.StopExtraction("API request failed")

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            pagination = data["pagination"]
            if pagination["current_page"] >= pagination["total_pages"]:
                return
            params["page"] = pagination["current_page"] + 1
