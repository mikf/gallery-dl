# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import util, exception


class ArcaliveAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.root = f"{extractor.root}/api/app"

        extractor.session.headers["X-Device-Token"] = util.generate_token(64)

    def board(self, board_slug, params):
        endpoint = f"/list/channel/{board_slug}"
        return self._pagination(endpoint, params, "articles")

    def post(self, post_id):
        endpoint = f"/view/article/breaking/{post_id}"
        return self._call(endpoint)

    def user_posts(self, username, params):
        endpoint = "/list/channel/breaking"
        params["target"] = "nickname"
        params["keyword"] = username
        return self._pagination(endpoint, params, "articles")

    def _call(self, endpoint, params=None):
        url = f"{self.root}{endpoint}"
        response = self.extractor.request(url, params=params)

        data = response.json()
        if response.status_code == 200:
            return data

        self.log.debug("Server response: %s", data)
        msg = f": {msg}" if (msg := data.get("message")) else ""
        raise exception.AbortExtraction(f"API request failed{msg}")

    def _pagination(self, endpoint, params, key):
        while True:
            data = self._call(endpoint, params)

            posts = data.get(key)
            if not posts:
                break
            yield from posts

            params.update(data["next"])
