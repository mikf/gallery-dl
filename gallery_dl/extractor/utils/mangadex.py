# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache, memcache


@cache(maxage=90*86400, keyarg=0)
def _refresh_token_cache(username):
    return None


class MangadexAPI():
    """Interface for the MangaDex API v5

    https://api.mangadex.org/docs/
    """

    def __init__(self, extr):
        self.extractor = extr
        self.headers = None
        self.headers_auth = {}

        self.username, self.password = extr._get_auth_info()
        if self.username:
            self.client_id = cid = extr.config("client-id")
            self.client_secret = extr.config("client-secret")
            if cid:
                self._authenticate_impl = self._authenticate_impl_client
            else:
                self._authenticate_impl = self._authenticate_impl_legacy
        else:
            self.authenticate = util.noop

        server = extr.config("api-server")
        self.root = ("https://api.mangadex.org" if server is None
                     else text.ensure_http_scheme(server).rstrip("/"))

    def athome_server(self, uuid):
        return self._call(f"/at-home/server/{uuid}")

    def author(self, uuid, manga=False):
        params = {"includes[]": ("manga",)} if manga else None
        return self._call(f"/author/{uuid}", params)["data"]

    def chapter(self, uuid):
        params = {"includes[]": ("scanlation_group",)}
        return self._call(f"/chapter/{uuid}", params)["data"]

    def covers_manga(self, uuid):
        params = {"manga[]": uuid}
        return self._pagination_covers("/cover", params)

    def list(self, uuid):
        return self._call(f"/list/{uuid}", None, True)["data"]

    def list_feed(self, uuid):
        return self._pagination_chapters(f"/list/{uuid}/feed", None, True)

    @memcache(keyarg=1)
    def manga(self, uuid):
        params = {"includes[]": ("artist", "author")}
        return self._call(f"/manga/{uuid}", params)["data"]

    def manga_author(self, uuid_author):
        params = {"authorOrArtist": uuid_author}
        return self._pagination_manga("/manga", params)

    def manga_feed(self, uuid):
        order = "desc" if self.extractor.config("chapter-reverse") else "asc"
        params = {
            "order[volume]" : order,
            "order[chapter]": order,
        }
        return self._pagination_chapters(f"/manga/{uuid}/feed", params)

    def user_follows_manga(self):
        params = {"contentRating": None}
        return self._pagination_manga(
            "/user/follows/manga", params, True)

    def user_follows_manga_feed(self):
        params = {"order[publishAt]": "desc"}
        return self._pagination_chapters(
            "/user/follows/manga/feed", params, True)

    def authenticate(self):
        self.headers_auth["Authorization"] = \
            self._authenticate_impl(self.username, self.password)

    @cache(maxage=900, keyarg=1)
    def _authenticate_impl_client(self, username, password):
        if refresh_token := _refresh_token_cache((username, "personal")):
            self.extractor.log.info("Refreshing access token")
            data = {
                "grant_type"   : "refresh_token",
                "refresh_token": refresh_token,
                "client_id"    : self.client_id,
                "client_secret": self.client_secret,
            }
        else:
            self.extractor.log.info("Logging in as %s", username)
            data = {
                "grant_type"   : "password",
                "username"     : self.username,
                "password"     : self.password,
                "client_id"    : self.client_id,
                "client_secret": self.client_secret,
            }

        self.extractor.log.debug("Using client-id '%s…'", self.client_id[:24])
        url = ("https://auth.mangadex.org/realms/mangadex"
               "/protocol/openid-connect/token")
        data = self.extractor.request_json(
            url, method="POST", data=data, fatal=None)

        try:
            access_token = data["access_token"]
        except Exception:
            raise exception.AuthenticationError(data.get("error_description"))

        if refresh_token != data.get("refresh_token"):
            _refresh_token_cache.update(
                (username, "personal"), data["refresh_token"])

        return f"Bearer {access_token}"

    @cache(maxage=900, keyarg=1)
    def _authenticate_impl_legacy(self, username, password):
        if refresh_token := _refresh_token_cache(username):
            self.extractor.log.info("Refreshing access token")
            url = f"{self.root}/auth/refresh"
            json = {"token": refresh_token}
        else:
            self.extractor.log.info("Logging in as %s", username)
            url = f"{self.root}/auth/login"
            json = {"username": username, "password": password}

        self.extractor.log.debug("Using legacy login method")
        data = self.extractor.request_json(
            url, method="POST", json=json, fatal=None)
        if data.get("result") != "ok":
            raise exception.AuthenticationError()

        if refresh_token != data["token"]["refresh"]:
            _refresh_token_cache.update(username, data["token"]["refresh"])
        return f"Bearer {data['token']['session']}"

    def _call(self, endpoint, params=None, auth=False):
        url = f"{self.root}{endpoint}"
        headers = self.headers_auth if auth else self.headers

        while True:
            if auth:
                self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=headers, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                until = response.headers.get("X-RateLimit-Retry-After")
                self.extractor.wait(until=until)
                continue

            msg = ", ".join(f'{error["title"]}: "{error["detail"]}"'
                            for error in response.json()["errors"])
            raise exception.AbortExtraction(
                f"{response.status_code} {response.reason} ({msg})")

    def _pagination_chapters(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        lang = self.extractor.config("lang")
        if isinstance(lang, str) and "," in lang:
            lang = lang.split(",")
        params["translatedLanguage[]"] = lang
        params["includes[]"] = ("scanlation_group",)

        return self._pagination(endpoint, params, auth)

    def _pagination_manga(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        return self._pagination(endpoint, params, auth)

    def _pagination_covers(self, endpoint, params=None, auth=False):
        if params is None:
            params = {}

        lang = self.extractor.config("lang")
        if isinstance(lang, str) and "," in lang:
            lang = lang.split(",")
        params["locales"] = lang
        params["contentRating"] = None
        params["order[volume]"] = \
            "desc" if self.extractor.config("chapter-reverse") else "asc"

        return self._pagination(endpoint, params, auth)

    def _pagination(self, endpoint, params, auth=False):
        config = self.extractor.config

        if "contentRating" not in params:
            ratings = config("ratings")
            if ratings is None:
                ratings = ("safe", "suggestive", "erotica", "pornographic")
            elif isinstance(ratings, str):
                ratings = ratings.split(",")
            params["contentRating[]"] = ratings
        params["offset"] = 0

        if api_params := config("api-parameters"):
            params.update(api_params)

        while True:
            data = self._call(endpoint, params, auth)
            yield from data["data"]

            params["offset"] = data["offset"] + data["limit"]
            if params["offset"] >= data["total"]:
                return
