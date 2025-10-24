# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class PhilomenaAPI():
    """Interface for the Philomena API

    https://www.derpibooru.org/pages/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = f"{extractor.root}/api"

    def gallery(self, gallery_id):
        endpoint = "/v1/json/search/galleries"
        params = {"q": f"id:{gallery_id}"}
        return self._call(endpoint, params)["galleries"][0]

    def image(self, image_id):
        endpoint = f"/v1/json/images/{image_id}"
        return self._call(endpoint)["image"]

    def search(self, params):
        endpoint = "/v1/json/search/images"
        return self._pagination(endpoint, params)

    def _call(self, endpoint, params=None):
        url = f"{self.root}{endpoint}"

        while True:
            response = self.extractor.request(url, params=params, fatal=None)

            if response.status_code < 400:
                return response.json()

            if response.status_code == 429:
                self.extractor.wait(seconds=600)
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
            params["filter_id"] = extr.config_instance("filter_id") or "2"

        params["page"] = extr.page_start
        params["per_page"] = extr.per_page

        while True:
            data = self._call(endpoint, params)
            yield from data["images"]

            if len(data["images"]) < extr.per_page:
                return
            params["page"] += 1
