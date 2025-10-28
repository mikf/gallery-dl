# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import exception
from ...cache import cache


@cache(maxage=365*86400, keyarg=1, utils=True)
def _authenticate_impl(api, username, password):
    api.extractor.log.info("Logging in as %s", username)

    url = "https://inkbunny.net/api_login.php"
    data = {"username": username, "password": password}
    data = api.extractor.request_json(url, method="POST", data=data)

    if "sid" not in data:
        raise exception.AuthenticationError(data.get("error_message"))
    return data["sid"]


class InkbunnyAPI():
    """Interface for the Inkunny API

    https://wiki.inkbunny.net/wiki/API
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.session_id = None

    def detail(self, submissions):
        """Get full details about submissions with the given IDs"""
        ids = {
            sub["submission_id"]: idx
            for idx, sub in enumerate(submissions)
        }
        params = {
            "submission_ids": ",".join(ids),
            "show_description": "yes",
            "show_pools": "yes",
        }

        submissions = [None] * len(ids)
        for sub in self._call("submissions", params)["submissions"]:
            submissions[ids[sub["submission_id"]]] = sub
        return submissions

    def search(self, params):
        """Perform a search"""
        return self._pagination_search(params)

    def set_allowed_ratings(self, nudity=True, sexual=True,
                            violence=True, strong_violence=True):
        """Change allowed submission ratings"""
        params = {
            "tag[2]": "yes" if nudity else "no",
            "tag[3]": "yes" if violence else "no",
            "tag[4]": "yes" if sexual else "no",
            "tag[5]": "yes" if strong_violence else "no",
        }
        self._call("userrating", params)

    def authenticate(self, invalidate=False):
        username, password = self.extractor._get_auth_info()
        if invalidate:
            _authenticate_impl.invalidate(username or "guest")
        if username:
            self.session_id = _authenticate_impl(self, username, password)
        else:
            self.session_id = _authenticate_impl(self, "guest", "")
            self.set_allowed_ratings()

    def _call(self, endpoint, params):
        url = f"https://inkbunny.net/api_{endpoint}.php"

        while True:
            params["sid"] = self.session_id
            data = self.extractor.request_json(url, params=params)

            if "error_code" not in data:
                return data

            if str(data["error_code"]) == "2":
                self.authenticate(invalidate=True)
                continue

            raise exception.AbortExtraction(data.get("error_message"))

    def _pagination_search(self, params):
        params["page"] = 1
        params["get_rid"] = "yes"
        params["submission_ids_only"] = "yes"

        while True:
            data = self._call("search", params)
            if not data["submissions"]:
                return

            yield from self.detail(data["submissions"])

            if data["page"] >= data["pages_count"]:
                return
            if "get_rid" in params:
                del params["get_rid"]
                params["rid"] = data["rid"]
            params["page"] += 1
