# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache


TAG_TYPES = {
    0: "general",
    1: "artist",
    2: "studio",
    3: "copyright",
    4: "character",
    5: "genre",
    6: "",
    7: "",
    8: "medium",
    9: "meta",
}


@cache(maxage=365*86400, keyarg=1, utils=True)
def _authenticate_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    api = extr.api
    url = f"{api.ROOT}/auth/token"
    data = {"login": username, "password": password}

    response = extr.request(
        url, method="POST", headers=api.headers, json=data, fatal=False)
    data = response.json()

    if response.status_code >= 400 or not data.get("success"):
        raise exception.AuthenticationError(data.get("error"))
    return f"Bearer {data['access_token']}"


class SankakuAPI():
    """Interface for the sankaku.app API"""
    ROOT = "https://sankakuapi.com"
    VERSION = None

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "Accept"     : "application/vnd.sankaku.api+json;v=2",
            "Api-Version": self.VERSION,
            "Origin"     : extractor.root,
        }

        self.username, self.password = extractor._get_auth_info()
        if not self.username:
            self.authenticate = util.noop

    def notes(self, post_id):
        params = {"lang": "en"}
        return self._call(f"/posts/{post_id}/notes", params)

    def tags(self, post_id):
        endpoint = f"/posts/{post_id}/tags"
        params = {
            "lang" : "en",
            "page" : 1,
            "limit": 100,
        }

        tags = None
        while True:
            data = self._call(endpoint, params)

            tags_new = data["data"]
            if not tags_new:
                return tags or []
            elif tags is None:
                tags = tags_new
            else:
                tags.extend(tags_new)

            if len(tags_new) < 80 or len(tags) >= data["total"]:
                return tags
            params["page"] += 1

    def pools(self, pool_id):
        params = {"lang": "en"}
        return self._call(f"/pools/{pool_id}", params)

    def pools_keyset(self, params):
        return self._pagination("/pools/keyset", params)

    def pools_series(self, params):
        params_ = {
            "lang"       : "en",
            "filledPools": "true",
            "includes[]" : "pools",
        }
        params_.update(params)
        return self._pagination("/poolseriesv2", params)

    def posts(self, post_id):
        params = {
            "lang" : "en",
            "page" : "1",
            "limit": "1",
            "tags" : ("md5:" if len(post_id) == 32 else "id_range:") + post_id,
        }
        return self._call("/v2/posts", params)

    def posts_keyset(self, params):
        return self._pagination("/v2/posts/keyset", params)

    def authenticate(self):
        self.headers["Authorization"] = \
            _authenticate_impl(self.extractor, self.username, self.password)

    def _call(self, endpoint, params=None):
        url = self.ROOT + endpoint
        for _ in range(5):
            self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code == 429:
                until = response.headers.get("X-RateLimit-Reset")
                if not until and b"_tags-explicit-limit" in response.content:
                    raise exception.AuthorizationError(
                        "Search tag limit exceeded")
                seconds = None if until else 600
                self.extractor.wait(until=until, seconds=seconds)
                continue

            data = response.json()
            try:
                success = data.get("success", True)
            except AttributeError:
                success = True
            if not success:
                code = data.get("code")
                if code and code.endswith(
                        ("unauthorized", "invalid-token", "invalid_token")):
                    _authenticate_impl.invalidate(self.username)
                    continue
                try:
                    code = f"'{code.rpartition('__')[2].replace('-', ' ')}'"
                except Exception:
                    pass
                raise exception.AbortExtraction(code)
            return data

    def _pagination(self, endpoint, params):
        params["lang"] = "en"
        params["limit"] = str(self.extractor.per_page)

        if refresh := self.extractor.config("refresh", False):
            offset = expires = 0
            from time import time

        while True:
            data = self._call(endpoint, params)

            if refresh:
                posts = data["data"]
                if offset:
                    posts = util.advance(posts, offset)

                for post in posts:
                    if not expires:
                        if url := post["file_url"]:
                            expires = text.parse_int(
                                text.extr(url, "e=", "&")) - 60

                    if 0 < expires <= time():
                        self.extractor.log.debug("Refreshing download URLs")
                        expires = None
                        break

                    offset += 1
                    yield post

                if expires is None:
                    expires = 0
                    continue
                offset = expires = 0

            else:
                yield from data["data"]

            params["next"] = data["meta"]["next"]
            if not params["next"]:
                return
