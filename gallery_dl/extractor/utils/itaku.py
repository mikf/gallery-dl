# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ...cache import memcache


class ItakuAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = extractor.root + "/api"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
        }

    def galleries_images(self, params, path=""):
        endpoint = f"/galleries/images{path}/"
        params = {
            "cursor"    : None,
            "date_range": "",
            "maturity_rating": ("SFW", "Questionable", "NSFW"),
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "30",
            "visibility": ("PUBLIC", "PROFILE_ONLY"),
            **params,
        }
        return self._pagination(endpoint, params, self.image)

    def posts(self, params):
        endpoint = "/posts/"
        params = {
            "cursor"    : None,
            "date_range": "",
            "maturity_rating": ("SFW", "Questionable", "NSFW"),
            "ordering"  : "-date_added",
            "page"      : "1",
            "page_size" : "30",
            **params,
        }
        return self._pagination(endpoint, params)

    def user_profiles(self, params):
        endpoint = "/user_profiles/"
        params = {
            "cursor"   : None,
            "ordering" : "-date_added",
            "page"     : "1",
            "page_size": "50",
            "sfw_only" : "false",
            **params,
        }
        return self._pagination(endpoint, params)

    def image(self, image_id):
        endpoint = f"/galleries/images/{image_id}/"
        return self._call(endpoint)

    def post(self, post_id):
        endpoint = f"/posts/{post_id}/"
        return self._call(endpoint)

    @memcache(keyarg=1)
    def user(self, username):
        return self._call(f"/user_profiles/{username}/")

    def user_id(self, username):
        if username.startswith("id:"):
            return int(username[3:])
        return self.user(username)["owner"]

    def _call(self, endpoint, params=None):
        if not endpoint.startswith("http"):
            endpoint = self.root + endpoint
        return self.extractor.request_json(
            endpoint, params=params, headers=self.headers)

    def _pagination(self, endpoint, params, extend=None):
        data = self._call(endpoint, params)

        while True:
            if extend is None:
                yield from data["results"]
            else:
                for result in data["results"]:
                    yield extend(result["id"])

            url_next = data["links"].get("next")
            if not url_next:
                return

            data = self._call(url_next)
