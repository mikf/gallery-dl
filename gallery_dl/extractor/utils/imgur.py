# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception


class ImgurAPI():
    """Interface for the Imgur API

    https://apidocs.imgur.com/
    """
    def __init__(self, extractor):
        self.extractor = extractor
        self.client_id = extractor.config("client-id") or "546c25a59c58ad7"
        self.headers = {"Authorization": f"Client-ID {self.client_id}"}

    def account_submissions(self, account):
        endpoint = f"/3/account/{account}/submissions"
        return self._pagination(endpoint)

    def account_favorites(self, account):
        endpoint = f"/3/account/{account}/gallery_favorites"
        return self._pagination(endpoint)

    def account_favorites_folder(self, account, folder_id):
        endpoint = f"/3/account/{account}/folders/{folder_id}/favorites"
        return self._pagination_v2(endpoint)

    def accounts_me_allposts(self):
        endpoint = "/post/v1/accounts/me/all_posts"
        params = {
            "include": "media,tags,account",
            "page"   : 1,
            "sort"   : "-created_at",
        }
        return self._pagination_v2(endpoint, params)

    def accounts_me_hiddenalbums(self):
        endpoint = "/post/v1/accounts/me/hidden_albums"
        params = {
            "include": "media,tags,account",
            "page"   : 1,
            "sort"   : "-created_at",
        }
        return self._pagination_v2(endpoint, params)

    def gallery_search(self, query):
        endpoint = "/3/gallery/search"
        params = {"q": query}
        return self._pagination(endpoint, params)

    def gallery_subreddit(self, subreddit):
        endpoint = f"/3/gallery/r/{subreddit}"
        return self._pagination(endpoint)

    def gallery_tag(self, tag):
        endpoint = f"/3/gallery/t/{tag}"
        return self._pagination(endpoint, key="items")

    def image(self, image_hash):
        endpoint = f"/post/v1/media/{image_hash}"
        params = {"include": "media,tags,account"}
        return self._call(endpoint, params)

    def album(self, album_hash):
        endpoint = f"/post/v1/albums/{album_hash}"
        params = {"include": "media,tags,account"}
        return self._call(endpoint, params)

    def gallery(self, gallery_hash):
        endpoint = f"/post/v1/posts/{gallery_hash}"
        return self._call(endpoint)

    def _call(self, endpoint, params=None, headers=None):
        while True:
            try:
                return self.extractor.request_json(
                    f"https://api.imgur.com{endpoint}",
                    params=params, headers=(headers or self.headers))
            except exception.HttpError as exc:
                if exc.status not in (403, 429) or \
                        b"capacity" not in exc.response.content:
                    raise
            self.extractor.wait(seconds=600)

    def _pagination(self, endpoint, params=None, key=None):
        num = 0

        while True:
            data = self._call(f"{endpoint}/{num}", params)["data"]
            if key:
                data = data[key]
            if not data:
                return
            yield from data
            num += 1

    def _pagination_v2(self, endpoint, params=None, key=None):
        if params is None:
            params = {}
        params["client_id"] = self.client_id
        if "page" not in params:
            params["page"] = 0
        if "sort" not in params:
            params["sort"] = "newest"
        headers = {"Origin": "https://imgur.com"}

        while True:
            data = self._call(endpoint, params, headers)
            if "data" in data:
                data = data["data"]
            if not data:
                return
            yield from data

            params["page"] += 1
