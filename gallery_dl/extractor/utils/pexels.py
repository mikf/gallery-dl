# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


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
        endpoint = f"/v3/collections/{collection_id}/media"
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
        endpoint = f"/v3/users/{user_id}/media/recent"
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
                raise exception.AbortExtraction("API request failed")

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            pagination = data["pagination"]
            if pagination["current_page"] >= pagination["total_pages"]:
                return
            params["page"] = pagination["current_page"] + 1
