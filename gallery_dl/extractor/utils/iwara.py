# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache, memcache
import hashlib


@cache(maxage=28*86400, keyarg=0, utils=True)
def _refresh_token_cache(username):
    return None


class IwaraAPI():
    """Interface for the Iwara API"""
    root = "https://api.iwara.tv"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Referer"     : f"{extractor.root}/",
            "Content-Type": "application/json",
            "Origin"      : extractor.root,
        }

        self.username, self.password = extractor._get_auth_info()
        if not self.username:
            self.authenticate = util.noop

    def image(self, image_id):
        endpoint = f"/image/{image_id}"
        return self._call(endpoint)

    def video(self, video_id):
        endpoint = f"/video/{video_id}"
        return self._call(endpoint)

    def playlist(self, playlist_id):
        endpoint = f"/playlist/{playlist_id}"
        return self._pagination(endpoint)

    def detail(self, media):
        endpoint = f"/{media['type']}/{media['id']}"
        return self._call(endpoint)

    def images(self, params):
        endpoint = "/images"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def videos(self, params):
        endpoint = "/videos"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def playlists(self, params):
        endpoint = "/playlists"
        return self._pagination(endpoint, params)

    def media(self, type, params):
        endpoint = f"/{type}s"
        params.setdefault("rating", "all")
        return self._pagination(endpoint, params)

    def favorites(self, type):
        if not self.username:
            raise exception.AuthRequired(
                "username & password", "your favorites")
        endpoint = f"/favorites/{type}s"
        return self._pagination(endpoint)

    def search(self, type, query):
        endpoint = "/search"
        params = {"type": type, "query": query}
        return self._pagination(endpoint, params)

    @memcache(keyarg=1)
    def profile(self, username):
        endpoint = f"/profile/{username}"
        return self._call(endpoint)

    def user_following(self, user_id):
        endpoint = f"/user/{user_id}/following"
        return self._pagination(endpoint)

    def user_followers(self, user_id):
        endpoint = f"/user/{user_id}/followers"
        return self._pagination(endpoint)

    def source(self, file_url):
        base, _, query = file_url.partition("?")
        if not (expires := text.extr(query, "expires=", "&")):
            return ()
        file_id = base.rpartition("/")[2]
        sha_postfix = "5nFp9kmbNnHdAFhaqMvt"
        sha_key = f"{file_id}_{expires}_{sha_postfix}"
        hash = hashlib.sha1(sha_key.encode()).hexdigest()
        headers = {"X-Version": hash, **self.headers}
        return self.extractor.request_json(file_url, headers=headers)

    def authenticate(self):
        self.headers["Authorization"] = self._authenticate_impl(self.username)

    @cache(maxage=3600, keyarg=1, utils=True)
    def _authenticate_impl(self, username):
        refresh_token = _refresh_token_cache(username)
        if refresh_token is None:
            self.extractor.log.info("Logging in as %s", username)

            url = f"{self.root}/user/login"
            json = {
                "email"   : username,
                "password": self.password
            }
            data = self.extractor.request_json(
                url, method="POST", headers=self.headers, json=json,
                fatal=False)

            if not (refresh_token := data.get("token")):
                self.extractor.log.debug(data)
                raise exception.AuthenticationError(data.get("message"))
            _refresh_token_cache.update(username, refresh_token)

        self.extractor.log.info("Refreshing access token for %s", username)

        url = f"{self.root}/user/token"
        headers = {"Authorization": f"Bearer {refresh_token}", **self.headers}
        data = self.extractor.request_json(
            url, method="POST", headers=headers, fatal=False)

        if not (access_token := data.get("accessToken")):
            self.extractor.log.debug(data)
            raise exception.AuthenticationError(data.get("message"))
        return f"Bearer {access_token}"

    def _call(self, endpoint, params=None, headers=None):
        self.authenticate()

        url = f"{self.root}{endpoint}"
        if headers is None:
            headers = self.headers
        return self.extractor.request_json(url, params=params, headers=headers)

    def _pagination(self, endpoint, params=None):
        if params is None:
            params = {}
        params["page"] = 0
        params["limit"] = 50

        while True:
            data = self._call(endpoint, params)

            if not (results := data.get("results")):
                break
            yield from results

            if len(results) < params["limit"]:
                break
            params["page"] += 1
