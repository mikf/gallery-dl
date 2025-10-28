# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception
from ...cache import cache


@cache(maxage=36500*86400, keyarg=0, utils=True)
def _access_token_cache(instance):
    return None


class MastodonAPI():
    """Minimal interface for the Mastodon API

    https://docs.joinmastodon.org/
    https://github.com/tootsuite/mastodon
    """

    def __init__(self, extractor):
        self.root = extractor.root
        self.extractor = extractor

        access_token = extractor.config("access-token")
        if access_token is None or access_token == "cache":
            access_token = _access_token_cache(extractor.instance)
        if not access_token:
            access_token = extractor.config_instance("access-token")

        if access_token:
            self.headers = {"Authorization": f"Bearer {access_token}"}
        else:
            self.headers = None

    def account_id_by_username(self, username):
        if username.startswith("id:"):
            return username[3:]

        try:
            return self.account_lookup(username)["id"]
        except Exception:
            # fall back to account search
            pass

        if "@" in username:
            handle = f"@{username}"
        else:
            handle = f"@{username}@{self.extractor.instance}"

        for account in self.account_search(handle, 1):
            if account["acct"] == username:
                self.extractor._check_moved(account)
                return account["id"]
        raise exception.NotFoundError("account")

    def account_bookmarks(self):
        """Statuses the user has bookmarked"""
        endpoint = "/v1/bookmarks"
        return self._pagination(endpoint, None)

    def account_favorites(self):
        """Statuses the user has favourited"""
        endpoint = "/v1/favourites"
        return self._pagination(endpoint, None)

    def account_following(self, account_id):
        """Accounts which the given account is following"""
        endpoint = f"/v1/accounts/{account_id}/following"
        return self._pagination(endpoint, None)

    def account_lookup(self, username):
        """Quickly lookup a username to see if it is available"""
        endpoint = "/v1/accounts/lookup"
        params = {"acct": username}
        return self._call(endpoint, params).json()

    def account_search(self, query, limit=40):
        """Search for matching accounts by username or display name"""
        endpoint = "/v1/accounts/search"
        params = {"q": query, "limit": limit}
        return self._call(endpoint, params).json()

    def account_statuses(self, account_id, only_media=True,
                         exclude_replies=False):
        """Statuses posted to the given account"""
        endpoint = f"/v1/accounts/{account_id}/statuses"
        params = {"only_media"     : "true" if only_media else "false",
                  "exclude_replies": "true" if exclude_replies else "false"}
        return self._pagination(endpoint, params)

    def status(self, status_id):
        """Obtain information about a status"""
        endpoint = f"/v1/statuses/{status_id}"
        return self._call(endpoint).json()

    def timelines_list(self, list_id):
        """View statuses in the given list timeline"""
        endpoint = f"/v1/timelines/list/{list_id}"
        return self._pagination(endpoint, None)

    def timelines_tag(self, hashtag):
        """View public statuses containing the given hashtag"""
        endpoint = f"/v1/timelines/tag/{hashtag}"
        return self._pagination(endpoint, None)

    def _call(self, endpoint, params=None):
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.root}/api{endpoint}"

        while True:
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)
            code = response.status_code

            if code < 400:
                return response
            if code == 401:
                raise exception.AbortExtraction(
                    f"Invalid or missing access token.\nRun 'gallery-dl oauth:"
                    f"mastodon:{self.extractor.instance}' to obtain one.")
            if code == 404:
                raise exception.NotFoundError()
            if code == 429:
                self.extractor.wait(until=self.parse_datetime_iso(
                    response.headers["x-ratelimit-reset"]))
                continue
            raise exception.AbortExtraction(response.json().get("error"))

    def _pagination(self, endpoint, params):
        url = endpoint
        while url:
            response = self._call(url, params)
            yield from response.json()

            url = response.links.get("next")
            if not url:
                return
            url = url["url"]
            params = None
