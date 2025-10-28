# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class LofterAPI():

    def __init__(self, extractor):
        self.extractor = extractor

    def blog_posts(self, blog_name):
        endpoint = "/v2.0/blogHomePage.api"
        params = {
            "method": "getPostLists",
            "offset": 0,
            "limit": 200,
            "blogdomain": f"{blog_name}.lofter.com",
        }
        return self._pagination(endpoint, params)

    def post(self, blog_id, post_id):
        endpoint = "/oldapi/post/detail.api"
        params = {
            "targetblogid": blog_id,
            "postid": post_id,
        }
        return self._call(endpoint, params)["posts"][0]

    def _call(self, endpoint, data):
        url = f"https://api.lofter.com{endpoint}"
        params = {
            'product': 'lofter-android-7.9.10'
        }
        response = self.extractor.request(
            url, method="POST", params=params, data=data)
        info = response.json()

        if info["meta"]["status"] == 4200:
            raise exception.NotFoundError("blog")

        if info["meta"]["status"] != 200:
            self.extractor.log.debug("Server response: %s", info)
            raise exception.AbortExtraction("API request failed")

        return info["response"]

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            posts = data["posts"]

            yield from posts

            if data["offset"] < 0:
                break

            if params["offset"] + len(posts) < data["offset"]:
                break
            params["offset"] = data["offset"]
