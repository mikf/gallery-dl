# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, dt, exception
from ...cache import cache, memcache
import hashlib


@cache(maxage=36500*86400, keyarg=0, utils=True)
def _refresh_token_cache(username):
    return None


class PixivAppAPI():
    """Minimal interface for the Pixiv App API for mobile devices

    For a more complete implementation or documentation, see
    - https://github.com/upbit/pixivpy
    - https://gist.github.com/ZipFile/3ba99b47162c23f8aea5d5942bb557b1
    """
    CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"
    HASH_SECRET = ("28c1fdd170a5204386cb1313c7077b34"
                   "f83e4aaf4aa829ce78c231e05b0bae2c")

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.username = extractor._get_auth_info()[0]
        self.user = None

        extractor.headers_web = extractor.session.headers.copy()
        extractor.session.headers.update({
            "App-OS"        : "ios",
            "App-OS-Version": "16.7.2",
            "App-Version"   : "7.19.1",
            "User-Agent"    : "PixivIOSApp/7.19.1 (iOS 16.7.2; iPhone12,8)",
            "Referer"       : "https://app-api.pixiv.net/",
        })

        self.client_id = extractor.config(
            "client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

        token = extractor.config("refresh-token")
        if token is None or token == "cache":
            token = _refresh_token_cache(self.username)
        self.refresh_token = token

    def login(self):
        """Login and gain an access token"""
        self.user, auth = self._login_impl(self.username)
        self.extractor.session.headers["Authorization"] = auth

    @cache(maxage=3600, keyarg=1, utils=True)
    def _login_impl(self, username):
        if not self.refresh_token:
            raise exception.AuthenticationError(
                "'refresh-token' required.\n"
                "Run `gallery-dl oauth:pixiv` to get one.")

        self.log.info("Refreshing access token")
        url = "https://oauth.secure.pixiv.net/auth/token"
        data = {
            "client_id"     : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type"    : "refresh_token",
            "refresh_token" : self.refresh_token,
            "get_secure_url": "1",
        }

        time = dt.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            "X-Client-Time": time,
            "X-Client-Hash": hashlib.md5(
                (time + self.HASH_SECRET).encode()).hexdigest(),
        }

        response = self.extractor.request(
            url, method="POST", headers=headers, data=data, fatal=False)
        if response.status_code >= 400:
            self.log.debug(response.text)
            raise exception.AuthenticationError("Invalid refresh token")

        data = response.json()["response"]
        return data["user"], "Bearer " + data["access_token"]

    def illust_detail(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("/v1/illust/detail", params)["illust"]

    def illust_bookmark_detail(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call(
            "/v2/illust/bookmark/detail", params)["bookmark_detail"]

    def illust_comments(self, illust_id):
        params = {"illust_id": illust_id}
        return self._pagination("/v3/illust/comments", params, "comments")

    def illust_follow(self, restrict="all"):
        params = {"restrict": restrict}
        return self._pagination("/v2/illust/follow", params)

    def illust_ranking(self, mode="day", date=None):
        params = {"mode": mode, "date": date}
        return self._pagination("/v1/illust/ranking", params)

    def illust_related(self, illust_id):
        params = {"illust_id": illust_id}
        return self._pagination("/v2/illust/related", params)

    def illust_series(self, series_id, offset=0):
        params = {"illust_series_id": series_id, "offset": offset}
        return self._pagination("/v1/illust/series", params,
                                key_data="illust_series_detail")

    def novel_bookmark_detail(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call(
            "/v2/novel/bookmark/detail", params)["bookmark_detail"]

    def novel_comments(self, novel_id):
        params = {"novel_id": novel_id}
        return self._pagination("/v1/novel/comments", params, "comments")

    def novel_detail(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call("/v2/novel/detail", params)["novel"]

    def novel_series(self, series_id):
        params = {"series_id": series_id}
        return self._pagination("/v1/novel/series", params, "novels")

    def novel_text(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call("/v1/novel/text", params)

    def novel_webview(self, novel_id):
        params = {"id": novel_id, "viewer_version": "20221031_ai"}
        return self._call(
            "/webview/v2/novel", params, self._novel_webview_parse)

    def _novel_webview_parse(self, response):
        return util.json_loads(text.extr(
            response.text, "novel: ", ",\n"))

    def search_illust(self, word, sort=None, target=None, duration=None,
                      date_start=None, date_end=None):
        params = {"word": word, "search_target": target,
                  "sort": sort, "duration": duration,
                  "start_date": date_start, "end_date": date_end}
        return self._pagination_search("/v1/search/illust", params)

    def user_bookmarks_illust(self, user_id, tag=None, restrict="public"):
        """Return illusts bookmarked by a user"""
        params = {"user_id": user_id, "tag": tag, "restrict": restrict}
        return self._pagination("/v1/user/bookmarks/illust", params)

    def user_bookmarks_novel(self, user_id, tag=None, restrict="public"):
        """Return novels bookmarked by a user"""
        params = {"user_id": user_id, "tag": tag, "restrict": restrict}
        return self._pagination("/v1/user/bookmarks/novel", params, "novels")

    def user_bookmark_tags_illust(self, user_id, restrict="public"):
        """Return bookmark tags defined by a user"""
        params = {"user_id": user_id, "restrict": restrict}
        return self._pagination(
            "/v1/user/bookmark-tags/illust", params, "bookmark_tags")

    @memcache(keyarg=1)
    def user_detail(self, user_id, fatal=True):
        params = {"user_id": user_id}
        return self._call("/v1/user/detail", params, fatal=fatal)

    def user_following(self, user_id, restrict="public"):
        params = {"user_id": user_id, "restrict": restrict}
        return self._pagination("/v1/user/following", params, "user_previews")

    def user_illusts(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("/v1/user/illusts", params, key_user="user")

    def user_novels(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("/v1/user/novels", params, "novels")

    def ugoira_metadata(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("/v1/ugoira/metadata", params)["ugoira_metadata"]

    def _call(self, endpoint, params=None, parse=None, fatal=True):
        url = "https://app-api.pixiv.net" + endpoint

        while True:
            self.login()
            response = self.extractor.request(url, params=params, fatal=False)

            if parse:
                data = parse(response)
            else:
                data = response.json()

            if "error" not in data or not fatal:
                return data

            self.log.debug(data)

            if response.status_code == 404:
                raise exception.NotFoundError()

            error = data["error"]
            if "rate limit" in (error.get("message") or "").lower():
                self.extractor.wait(seconds=300)
                continue

            msg = (f"'{msg}'" if (msg := error.get("user_message")) else
                   f"'{msg}'" if (msg := error.get("message")) else
                   error)
            raise exception.AbortExtraction(f"API request failed: {msg}")

    def _pagination(self, endpoint, params,
                    key_items="illusts", key_data=None, key_user=None):
        data = self._call(endpoint, params)

        if key_data is not None:
            self.data = data.get(key_data)
        if key_user is not None and not data[key_user].get("id"):
            user = self.user_detail(self.extractor.user_id, fatal=False)
            if user.get("error"):
                raise exception.NotFoundError("user")
            return

        while True:
            yield from data[key_items]

            if not data["next_url"]:
                return
            query = data["next_url"].rpartition("?")[2]
            params = text.parse_query(query)
            data = self._call(endpoint, params)

    def _pagination_search(self, endpoint, params):
        sort = params["sort"]
        if sort == "date_desc":
            date_key = "end_date"
            date_off = dt.timedelta(days=1)
            date_cmp = lambda lhs, rhs: lhs >= rhs  # noqa E731
        elif sort == "date_asc":
            date_key = "start_date"
            date_off = dt.timedelta(days=-1)
            date_cmp = lambda lhs, rhs: lhs <= rhs  # noqa E731
        else:
            date_key = None
        date_last = None

        while True:
            data = self._call(endpoint, params)

            if date_last is None:
                yield from data["illusts"]
            else:
                works = data["illusts"]
                if date_cmp(date_last, works[-1]["create_date"]):
                    for work in works:
                        if date_last is None:
                            yield work
                        elif date_cmp(date_last, work["create_date"]):
                            date_last = None

            if not (next_url := data.get("next_url")):
                return
            query = next_url.rpartition("?")[2]
            params = text.parse_query(query)

            if date_key and text.parse_int(params.get("offset")) >= 5000:
                date_last = data["illusts"][-1]["create_date"]
                date_val = (dt.parse_iso(date_last) + date_off).strftime(
                    "%Y-%m-%d")
                self.log.info("Reached 'offset' >= 5000; "
                              "Updating '%s' to '%s'", date_key, date_val)
                params[date_key] = date_val
                params.pop("offset", None)
