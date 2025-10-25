# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


def posts(self, user):
    url = f"{self.root}/api/posts"
    params = {
        "page"    : 1,
        "sort"    : "new",
        "tag"     : "",
        "q"       : "",
        "username": user,
        "nsfw"    : "true",
    }

    while True:
        try:
            data = self.request_json(url, params=params)["data"]
        except (TypeError, KeyError):
            return

        if not data:
            return
        yield from data

        params["page"] += 1


class ImagechestAPI():
    """Interface for the Image Chest API

    https://imgchest.com/docs/api/1.0/general/overview
    """
    root = "https://api.imgchest.com"

    def __init__(self, extractor, access_token):
        self.extractor = extractor
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def file(self, file_id):
        endpoint = f"/v1/file/{file_id}"
        return self._call(endpoint)

    def post(self, post_id):
        endpoint = f"/v1/post/{post_id}"
        return self._call(endpoint)

    def user(self, username):
        endpoint = f"/v1/user/{username}"
        return self._call(endpoint)

    def _call(self, endpoint):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, headers=self.headers, fatal=None, allow_redirects=False)

            if response.status_code < 300:
                return response.json()["data"]

            elif response.status_code < 400:
                raise exception.AuthenticationError("Invalid API access token")

            elif response.status_code == 429:
                self.extractor.wait(seconds=600)

            else:
                self.extractor.log.debug(response.text)
                raise exception.AbortExtraction("API request failed")
