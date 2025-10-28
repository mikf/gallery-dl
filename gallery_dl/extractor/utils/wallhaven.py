# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class WallhavenAPI():
    """Interface for wallhaven's API

    Ref: https://wallhaven.cc/help/api
    """

    def __init__(self, extractor):
        self.extractor = extractor

        key = extractor.config("api-key")
        if key is None:
            key = "25HYZenXTICjzBZXzFSg98uJtcQVrDs2"
            extractor.log.debug("Using default API Key")
        else:
            extractor.log.debug("Using custom API Key")
        self.headers = {"X-API-Key": key}

    def info(self, wallpaper_id):
        endpoint = "/v1/w/" + wallpaper_id
        return self._call(endpoint)["data"]

    def collection(self, username, collection_id):
        endpoint = f"/v1/collections/{username}/{collection_id}"
        return self._pagination(endpoint)

    def collections(self, username):
        endpoint = "/v1/collections/" + username
        return self._pagination(endpoint, metadata=False)

    def search(self, params):
        endpoint = "/v1/search"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = "https://wallhaven.cc/api" + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                self.extractor.wait(seconds=60)
                continue

            self.extractor.log.debug("Server response: %s", response.text)
            raise exception.AbortExtraction(
                f"API request failed "
                f"({response.status_code} {response.reason})")

    def _pagination(self, endpoint, params=None, metadata=None):
        if params is None:
            params_ptr = None
            params = {}
        else:
            params_ptr = params
            params = params.copy()
        if metadata is None:
            metadata = self.extractor.config("metadata")

        while True:
            data = self._call(endpoint, params)

            meta = data.get("meta")
            if params_ptr is not None:
                if meta and "query" in meta:
                    query = meta["query"]
                    if isinstance(query, dict):
                        params_ptr["tags"] = query.get("tag")
                        params_ptr["tag_id"] = query.get("id")
                    else:
                        params_ptr["tags"] = query
                        params_ptr["tag_id"] = 0
                params_ptr = None

            if metadata:
                for wp in data["data"]:
                    yield self.info(str(wp["id"]))
            else:
                yield from data["data"]

            if not meta or meta["current_page"] >= meta["last_page"]:
                return
            params["page"] = meta["current_page"] + 1
