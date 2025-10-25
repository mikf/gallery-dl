# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, exception


class BoostyAPI():
    """Interface for the Boosty API"""
    root = "https://api.boosty.to"

    def __init__(self, extractor, access_token=None):
        self.extractor = extractor
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": extractor.root,
        }

        if not access_token:
            if auth := self.extractor.cookies.get("auth", domain=".boosty.to"):
                access_token = text.extr(
                    text.unquote(auth), '"accessToken":"', '"')
        if access_token:
            self.headers["Authorization"] = "Bearer " + access_token

    def blog_posts(self, username, params):
        endpoint = f"/v1/blog/{username}/post/"
        params = self._merge_params(params, {
            "limit"         : "5",
            "offset"        : None,
            "comments_limit": "2",
            "reply_limit"   : "1",
        })
        return self._pagination(endpoint, params)

    def blog_media_album(self, username, type="all", params=()):
        endpoint = f"/v1/blog/{username}/media_album/"
        params = self._merge_params(params, {
            "type"    : type.rstrip("s"),
            "limit"   : "15",
            "limit_by": "media",
            "offset"  : None,
        })
        return self._pagination(endpoint, params, self._transform_media_posts)

    def _transform_media_posts(self, data):
        posts = []

        for obj in data["mediaPosts"]:
            post = obj["post"]
            post["data"] = obj["media"]
            posts.append(post)

        return posts

    def post(self, username, post_id):
        endpoint = f"/v1/blog/{username}/post/{post_id}"
        return self._call(endpoint)

    def feed_posts(self, params=None):
        endpoint = "/v1/feed/post/"
        params = self._merge_params(params, {
            "limit"         : "5",
            "offset"        : None,
            "comments_limit": "2",
        })
        if "only_allowed" not in params and self.extractor.only_allowed:
            params["only_allowed"] = "true"
        if "only_bought" not in params and self.extractor.only_bought:
            params["only_bought"] = "true"
        return self._pagination(endpoint, params, key="posts")

    def user(self, username):
        endpoint = "/v1/blog/" + username
        user = self._call(endpoint)
        user["id"] = user["owner"]["id"]
        return user

    def user_subscriptions(self, params=None):
        endpoint = "/v1/user/subscriptions"
        params = self._merge_params(params, {
            "limit"      : "30",
            "with_follow": "true",
            "offset"     : None,
        })
        return self._pagination_users(endpoint, params)

    def _merge_params(self, params_web, params_api):
        if params_web:
            web_to_api = {
                "isOnlyAllowedPosts": "is_only_allowed",
                "postsTagsIds"      : "tags_ids",
                "postsFrom"         : "from_ts",
                "postsTo"           : "to_ts",
            }
            for name, value in params_web.items():
                name = web_to_api.get(name, name)
                params_api[name] = value
        return params_api

    def _call(self, endpoint, params=None):
        url = self.root + endpoint

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers,
                fatal=None, allow_redirects=False)

            if response.status_code < 300:
                return response.json()

            elif response.status_code < 400:
                raise exception.AuthenticationError("Invalid API access token")

            elif response.status_code == 429:
                self.extractor.wait(seconds=600)

            else:
                self.extractor.log.debug(response.text)
                raise exception.AbortExtraction("API request failed")

    def _pagination(self, endpoint, params, transform=None, key=None):
        if "is_only_allowed" not in params and self.extractor.only_allowed:
            params["only_allowed"] = "true"
            params["is_only_allowed"] = "true"

        while True:
            data = self._call(endpoint, params)

            if transform:
                yield from transform(data["data"])
            elif key:
                yield from data["data"][key]
            else:
                yield from data["data"]

            extra = data["extra"]
            if extra.get("isLast"):
                return
            offset = extra.get("offset")
            if not offset:
                return
            params["offset"] = offset

    def _pagination_users(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            offset = data["offset"] + data["limit"]
            if offset > data["total"]:
                return
            params["offset"] = offset

    def dialog(self, dialog_id):
        endpoint = f"/v1/dialog/{dialog_id}"
        return self._call(endpoint)

    def dialog_messages(self, dialog_id, limit=300, offset=None):
        endpoint = f"/v1/dialog/{dialog_id}/message/"
        params = {
            "limit": limit,
            "reverse": "true",
            "offset": offset,
        }
        return self._pagination_dialog(endpoint, params)

    def _pagination_dialog(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)

            yield from data["data"]

            try:
                extra = data["extra"]
                if extra.get("isLast"):
                    break
                params["offset"] = offset = extra["offset"]
                if not offset:
                    break
            except Exception:
                break
