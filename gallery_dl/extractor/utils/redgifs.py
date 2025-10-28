# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ...cache import memcache


class RedgifsAPI():
    """https://api.redgifs.com/docs/index.html"""

    API_ROOT = "https://api.redgifs.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Accept"        : "application/json, text/plain, */*",
            "Referer"       : f"{extractor.root}/",
            "Authorization" : None,
            "Origin"        : extractor.root,
        }

    def gif(self, gif_id):
        endpoint = f"/v2/gifs/{gif_id.lower()}"
        return self._call(endpoint)["gif"]

    def gallery(self, gallery_id):
        endpoint = f"/v2/gallery/{gallery_id}"
        return self._call(endpoint)

    def user(self, user, order="new"):
        endpoint = f"/v2/users/{user.lower()}/search"
        params = {"order": order}
        return self._pagination(endpoint, params)

    def collection(self, user, collection_id):
        endpoint = f"/v2/users/{user}/collections/{collection_id}/gifs"
        return self._pagination(endpoint)

    def collection_info(self, user, collection_id):
        endpoint = f"/v2/users/{user}/collections/{collection_id}"
        return self._call(endpoint)

    def collections(self, user):
        endpoint = f"/v2/users/{user}/collections"
        return self._pagination(endpoint, key="collections")

    def niches(self, niche, order):
        endpoint = f"/v2/niches/{niche}/gifs"
        params = {"count": 30, "order": order}
        return self._pagination(endpoint, params)

    def gifs_search(self, params):
        endpoint = "/v2/gifs/search"
        params["search_text"] = params.pop("tags", None)
        return self._pagination(endpoint, params)

    def search_gifs(self, params):
        endpoint = "/v2/search/gifs"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = f"{self.API_ROOT}{endpoint}"
        self.headers["Authorization"] = self._auth()
        return self.extractor.request_json(
            url, params=params, headers=self.headers)

    def _pagination(self, endpoint, params=None, key="gifs"):
        if params is None:
            params = {}
        params["page"] = 1

        while True:
            data = self._call(endpoint, params)
            yield from data[key]

            if params["page"] >= data["pages"]:
                return
            params["page"] += 1

    @memcache(maxage=600)
    def _auth(self):
        # https://github.com/Redgifs/api/wiki/Temporary-tokens
        url = f"{self.API_ROOT}/v2/auth/temporary"
        self.headers["Authorization"] = None
        return f"Bearer {self.extractor.request_json(url, headers=self.headers)['token']}"
