# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import oauth, exception


NullUser = {
    "Uri": "",
    "ResponseLevel": "Public",
    "Name": "",
    "NickName": "",
    "QuickShare": False,
    "RefTag": "",
    "ViewPassHint": "",
    "WebUri": "",
    "Uris": None,
}


class SmugmugAPI(oauth.OAuth1API):
    """Minimal interface for the smugmug API v2"""
    API_DOMAIN = "api.smugmug.com"
    API_KEY = "RCVHDGjcbc4Fhzq4qzqLdZmvwmwB6LM2"
    API_SECRET = ("jGrdndvJqhTx8XSNs7TFTSSthhZHq92d"
                  "dMpbpDpkDVNM7TDgnvLFMtfB5Mg5kH73")
    HEADERS = {"Accept": "application/json"}

    def album(self, album_id, expands=None):
        return self._expansion("album/" + album_id, expands)

    def image(self, image_id, expands=None):
        return self._expansion("image/" + image_id, expands)

    def node(self, node_id, expands=None):
        return self._expansion("node/" + node_id, expands)

    def user(self, username, expands=None):
        return self._expansion("user/" + username, expands)

    def album_images(self, album_id, expands=None):
        return self._pagination("album/" + album_id + "!images", expands)

    def node_children(self, node_id, expands=None):
        return self._pagination("node/" + node_id + "!children", expands)

    def user_albums(self, username, expands=None):
        return self._pagination("user/" + username + "!albums", expands)

    def site_user(self, domain):
        return self._call("!siteuser", domain=domain)["Response"]["User"]

    def user_urlpathlookup(self, username, path):
        endpoint = "user/" + username + "!urlpathlookup"
        params = {"urlpath": path}
        return self._expansion(endpoint, "Node", params)

    def _call(self, endpoint, params=None, domain=API_DOMAIN):
        url = f"https://{domain}/api/v2/{endpoint}"
        params = params or {}
        if self.api_key:
            params["APIKey"] = self.api_key
        params["_verbosity"] = "1"

        response = self.request(url, params=params, headers=self.HEADERS)
        data = response.json()

        if 200 <= data["Code"] < 400:
            return data
        if data["Code"] == 404:
            raise exception.NotFoundError()
        if data["Code"] == 429:
            raise exception.AbortExtraction("Rate limit reached")
        self.log.debug(data)
        raise exception.AbortExtraction("API request failed")

    def _expansion(self, endpoint, expands, params=None):
        endpoint = self._extend(endpoint, expands)
        result = self._apply_expansions(self._call(endpoint, params), expands)
        if not result:
            raise exception.NotFoundError()
        return result[0]

    def _pagination(self, endpoint, expands=None):
        endpoint = self._extend(endpoint, expands)
        params = {"start": 1, "count": 100}

        while True:
            data = self._call(endpoint, params)
            yield from self._apply_expansions(data, expands)

            if "NextPage" not in data["Response"]["Pages"]:
                return
            params["start"] += params["count"]

    def _extend(self, endpoint, expands):
        if expands:
            endpoint += "?_expand=" + expands
        return endpoint

    def _apply_expansions(self, data, expands):

        def unwrap(response):
            locator = response["Locator"]
            return response[locator] if locator in response else []

        objs = unwrap(data["Response"])
        if not isinstance(objs, list):
            objs = (objs,)

        if "Expansions" in data:
            expansions = data["Expansions"]
            expands = expands.split(",")

            for obj in objs:
                uris = obj["Uris"]

                for name in expands:
                    if name in uris:
                        uri = uris[name]
                        uris[name] = unwrap(expansions[uri])

        return objs
