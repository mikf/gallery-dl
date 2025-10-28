# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import cache


@cache(maxage=36500*86400, keyarg=0, utils=True)
def _refresh_token_cache(token):
    if token and token[0] == "#":
        return None
    return token


class RedditAPI():
    """Interface for the Reddit API

    https://www.reddit.com/dev/api/
    """
    ROOT = "https://oauth.reddit.com"
    CLIENT_ID = "6N9uN0krSDE-ig"
    USER_AGENT = "Python:gallery-dl:0.8.4 (by /u/mikf1)"

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log

        config = extractor.config

        self.comments = text.parse_int(config("comments", 0))
        self.morecomments = config("morecomments", False)
        self._warn_429 = False

        if config("api") == "rest":
            self.root = "https://www.reddit.com"
            self.headers = None
            self.authenticate = util.noop
            self.log.debug("Using REST API")
        else:
            self.root = self.ROOT

            client_id = config("client-id")
            if client_id is None:
                self.client_id = self.CLIENT_ID
                self.headers = {"User-Agent": self.USER_AGENT}
            else:
                self.client_id = client_id
                self.headers = {"User-Agent": config("user-agent")}

            if self.client_id == self.CLIENT_ID:
                client_id = self.client_id
                self._warn_429 = True
                kind = "default"
            else:
                client_id = client_id[:5] + "*" * (len(client_id)-5)
                kind = "custom"

            self.log.debug(
                "Using %s API credentials (client-id %s)", kind, client_id)

            token = config("refresh-token")
            if token is None or token == "cache":
                key = "#" + self.client_id
                self.refresh_token = _refresh_token_cache(key)
            else:
                self.refresh_token = token

            if not self.refresh_token:
                # allow downloading from quarantined subreddits (#2180)
                extractor.cookies.set(
                    "_options", '%7B%22pref_quarantine_optin%22%3A%20true%7D',
                    domain=extractor.cookies_domain)

    def submission(self, submission_id):
        """Fetch the (submission, comments)=-tuple for a submission id"""
        endpoint = "/comments/" + submission_id + "/.json"
        link_id = "t3_" + submission_id if self.morecomments else None
        submission, comments = self._call(endpoint, {"limit": self.comments})
        return (submission["data"]["children"][0]["data"],
                self._flatten(comments, link_id) if self.comments else ())

    def submissions_subreddit(self, subreddit, params):
        """Collect all (submission, comments)-tuples of a subreddit"""
        endpoint = subreddit + "/.json"
        return self._pagination(endpoint, params)

    def submissions_user(self, user, params):
        """Collect all (submission, comments)-tuples posted by a user"""
        endpoint = "/user/" + user + "/.json"
        return self._pagination(endpoint, params)

    def morechildren(self, link_id, children):
        """Load additional comments from a submission"""
        endpoint = "/api/morechildren"
        params = {"link_id": link_id, "api_type": "json"}
        index, done = 0, False
        while not done:
            if len(children) - index < 100:
                done = True
            params["children"] = ",".join(children[index:index + 100])
            index += 100

            data = self._call(endpoint, params)["json"]
            for thing in data["data"]["things"]:
                if thing["kind"] == "more":
                    children.extend(thing["data"]["children"])
                else:
                    yield thing["data"]

    def authenticate(self):
        """Authenticate the application by requesting an access token"""
        self.headers["Authorization"] = \
            self._authenticate_impl(self.refresh_token)

    @cache(maxage=3600, keyarg=1, utils=True)
    def _authenticate_impl(self, refresh_token=None):
        """Actual authenticate implementation"""
        url = "https://www.reddit.com/api/v1/access_token"
        self.headers["Authorization"] = None

        if refresh_token:
            self.log.info("Refreshing private access token")
            data = {"grant_type": "refresh_token",
                    "refresh_token": refresh_token}
        else:
            self.log.info("Requesting public access token")
            data = {"grant_type": ("https://oauth.reddit.com/"
                                   "grants/installed_client"),
                    "device_id": "DO_NOT_TRACK_THIS_DEVICE"}

        auth = util.HTTPBasicAuth(self.client_id, "")
        response = self.extractor.request(
            url, method="POST", headers=self.headers,
            data=data, auth=auth, fatal=False)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError(
                f"\"{data.get('error')}: {data.get('message')}\"")
        return "Bearer " + data["access_token"]

    def _call(self, endpoint, params):
        url = f"{self.root}{endpoint}"
        params["raw_json"] = "1"

        while True:
            self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            remaining = response.headers.get("x-ratelimit-remaining")
            if remaining and float(remaining) < 2:
                self.log.warning("API rate limit exceeded")
                if self._warn_429 and self.client_id == self.CLIENT_ID:
                    self.log.info(
                        "Register your own OAuth application and use its "
                        "credentials to prevent this error: "
                        "https://gdl-org.github.io/docs/configuration.html"
                        "#extractor-reddit-client-id-user-agent")
                self._warn_429 = False
                self.extractor.wait(
                    seconds=response.headers["x-ratelimit-reset"])
                continue

            try:
                data = response.json()
            except ValueError:
                raise exception.AbortExtraction(
                    text.remove_html(response.text))

            if "error" in data:
                if data["error"] == 403:
                    raise exception.AuthorizationError()
                if data["error"] == 404:
                    raise exception.NotFoundError()
                self.log.debug(data)
                raise exception.AbortExtraction(data.get("message"))
            return data

    def _pagination(self, endpoint, params):
        id_min = self._parse_id("id-min", 0)
        id_max = self._parse_id("id-max", float("inf"))
        if id_max == 2147483647:
            self.log.debug("Ignoring 'id-max' setting \"zik0zj\"")
            id_max = float("inf")
        date_min, date_max = self.extractor._get_date_min_max(0, 253402210800)

        if limit := self.extractor.config("limit"):
            params["limit"] = limit

        while True:
            data = self._call(endpoint, params)["data"]

            for child in data["children"]:
                kind = child["kind"]
                post = child["data"]

                if (date_min <= post["created_utc"] <= date_max and
                        id_min <= self._decode(post["id"]) <= id_max):

                    if kind == "t3":
                        if post["num_comments"] and self.comments:
                            try:
                                yield self.submission(post["id"])
                            except exception.AuthorizationError:
                                pass
                        else:
                            yield post, ()

                    elif kind == "t1" and self.comments:
                        yield None, (post,)

            if not data["after"]:
                return
            params["after"] = data["after"]

    def _flatten(self, comments, link_id=None):
        extra = []
        queue = comments["data"]["children"]
        while queue:
            comment = queue.pop(0)
            if comment["kind"] == "more":
                if link_id:
                    extra.extend(comment["data"]["children"])
                continue
            comment = comment["data"]
            yield comment
            if comment["replies"]:
                queue += comment["replies"]["data"]["children"]
        if link_id and extra:
            yield from self.morechildren(link_id, extra)

    def _parse_id(self, key, default):
        sid = self.extractor.config(key)
        return self._decode(sid.rpartition("_")[2].lower()) if sid else default

    def _decode(self, sid):
        return util.bdecode(sid, "0123456789abcdefghijklmnopqrstuvwxyz")
