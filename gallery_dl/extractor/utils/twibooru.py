# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class TwibooruAPI():
    """Interface for the Twibooru API

    https://twibooru.org/pages/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = "https://twibooru.org/api"

    def gallery(self, gallery_id):
        endpoint = f"/v3/galleries/{gallery_id}"
        return self._call(endpoint)["gallery"]

    def post(self, post_id):
        endpoint = f"/v3/posts/{post_id}"
        return self._call(endpoint)["post"]

    def search(self, params):
        endpoint = "/v3/search/posts"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = f"{self.root}{endpoint}"

        while True:
            response = self.extractor.request(url, params=params, fatal=None)

            if response.status_code < 400:
                return response.json()

            if response.status_code == 429:
                until = self.parse_datetime_iso(
                    response.headers["X-RL-Reset"][:19])
                # wait an extra minute, just to be safe
                self.extractor.wait(until=until, adjust=60.0)
                continue

            # error
            self.extractor.log.debug(response.content)
            raise exception.HttpError("", response)

    def _pagination(self, endpoint, params):
        extr = self.extractor

        if api_key := extr.config("api-key"):
            params["key"] = api_key

        if filter_id := extr.config("filter"):
            params["filter_id"] = filter_id
        elif not api_key:
            params["filter_id"] = "2"

        params["page"] = extr.page_start
        params["per_page"] = per_page = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["posts"]

            if len(data["posts"]) < per_page:
                return
            params["page"] += 1
