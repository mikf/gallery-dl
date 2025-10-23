# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import oauth, text, dt, exception


class TumblrAPI(oauth.OAuth1API):
    """Interface for the Tumblr API v2

    https://github.com/tumblr/docs/blob/master/api.md
    """
    ROOT = "https://api.tumblr.com"
    API_KEY = "O3hU2tMi5e4Qs5t3vezEi6L0qRORJ5y9oUpSGsrWu8iA3UCc3B"
    API_SECRET = "sFdsK3PDdP2QpYMRAoq0oDnw0sFS24XigXmdfnaeNZpJpqAn03"
    BLOG_CACHE = {}

    def __init__(self, extractor):
        oauth.OAuth1API.__init__(self, extractor)
        self.posts_type = self.before = None

    def info(self, blog):
        """Return general information about a blog"""
        try:
            return self.BLOG_CACHE[blog]
        except KeyError:
            endpoint = f"/v2/blog/{blog}/info"
            params = {"api_key": self.api_key} if self.api_key else None
            self.BLOG_CACHE[blog] = blog = self._call(endpoint, params)["blog"]
            return blog

    def avatar(self, blog, size="512"):
        """Retrieve a blog avatar"""
        if self.api_key:
            return (f"{self.ROOT}/v2/blog/{blog}/avatar/{size}"
                    f"?api_key={self.api_key}")
        endpoint = f"/v2/blog/{blog}/avatar"
        params = {"size": size}
        return self._call(
            endpoint, params, allow_redirects=False)["avatar_url"]

    def posts(self, blog, params):
        """Retrieve published posts"""
        params["offset"] = self.extractor.config("offset")
        params["limit"] = 50
        params["reblog_info"] = "true"
        params["type"] = self.posts_type
        params["before"] = self.before

        if self.before and params["offset"]:
            self.log.warning("'offset' and 'date-max' cannot be used together")

        endpoint = f"/v2/blog/{blog}/posts"
        return self._pagination(endpoint, params, blog=blog, cache=True)

    def likes(self, blog):
        """Retrieve liked posts"""
        endpoint = f"/v2/blog/{blog}/likes"
        params = {"limit": "50", "before": self.before}
        if self.api_key:
            params["api_key"] = self.api_key

        while True:
            posts = self._call(endpoint, params)["liked_posts"]
            if not posts:
                return
            yield from posts
            params["before"] = posts[-1]["liked_timestamp"]

    def following(self, blog):
        endpoint = f"/v2/blog/{blog}/following"
        return self._pagination_blogs(endpoint)

    def followers(self, blog):
        endpoint = f"/v2/blog/{blog}/followers"
        return self._pagination_blogs(endpoint)

    def search(self, query, params, mode="top", post_type=None):
        """Retrieve search results"""
        endpoint = "/v2/timeline/search"

        params["limit"] = "50"
        params["days"] = params.pop("t", None)
        params["query"] = query
        params["mode"] = mode
        params["reblog_info"] = "true" if self.extractor.reblogs else "false"
        if post_type:
            params["post_type_filter"] = post_type

        return self._pagination(endpoint, params)

    def _call(self, endpoint, params, **kwargs):
        url = self.ROOT + endpoint
        kwargs["params"] = params

        while True:
            response = self.request(url, **kwargs)

            try:
                data = response.json()
            except ValueError:
                data = response.text
                status = response.status_code
            else:
                status = data["meta"]["status"]
                if 200 <= status < 400:
                    return data["response"]

            self.log.debug(data)

            if status == 403:
                raise exception.AuthorizationError()

            elif status == 404:
                try:
                    error = data["errors"][0]["detail"]
                    board = ("only viewable within the Tumblr dashboard"
                             in error)
                except Exception:
                    board = False

                if board:
                    if self.api_key is None:
                        self.log.info(
                            "Ensure your 'access-token' and "
                            "'access-token-secret' belong to the same "
                            "application as 'api-key' and 'api-secret'")
                    else:
                        self.log.info("Run 'gallery-dl oauth:tumblr' "
                                      "to access dashboard-only blogs")
                    raise exception.AuthorizationError(error)
                raise exception.NotFoundError("user or post")

            elif status == 429:
                # daily rate limit
                if response.headers.get("x-ratelimit-perday-remaining") == "0":
                    self.log.info("Daily API rate limit exceeded")
                    reset = response.headers.get("x-ratelimit-perday-reset")

                    api_key = self.api_key or self.session.auth.consumer_key
                    if api_key == self.API_KEY:
                        self.log.info(
                            "Register your own OAuth application and use its "
                            "credentials to prevent this error: "
                            "https://gdl-org.github.io/docs/configuration.html"
                            "#extractor-tumblr-api-key-api-secret")

                    if self.extractor.config("ratelimit") == "wait":
                        self.extractor.wait(seconds=reset)
                        continue

                    t = (dt.now() + dt.timedelta(0, float(reset))).time()
                    raise exception.AbortExtraction(
                        f"Aborting - Rate limit will reset at "
                        f"{t.hour:02}:{t.minute:02}:{t.second:02}")

                # hourly rate limit
                if reset := response.headers.get("x-ratelimit-perhour-reset"):
                    self.log.info("Hourly API rate limit exceeded")
                    self.extractor.wait(seconds=reset)
                    continue

            raise exception.AbortExtraction(data)

    def _pagination(self, endpoint, params,
                    blog=None, key="posts", cache=False):
        if self.api_key:
            params["api_key"] = self.api_key

        strategy = self.extractor.config("pagination")
        if not strategy:
            if params.get("before"):
                strategy = "before"
            elif "offset" not in params:
                strategy = "api"

        while True:
            data = self._call(endpoint, params)

            if "timeline" in data:
                data = data["timeline"]
                posts = data["elements"]

            else:
                if cache:
                    self.BLOG_CACHE[blog] = data["blog"]
                    cache = False
                posts = data[key]

            yield from posts

            if strategy == "api":
                try:
                    endpoint = data["_links"]["next"]["href"]
                except KeyError:
                    return
                if params is not None and self.api_key:
                    endpoint = f"{endpoint}&api_key={self.api_key}"
                    params = None

            elif strategy == "before":
                if not posts:
                    return
                timestamp = posts[-1]["timestamp"] + 1
                if params["before"] and timestamp >= params["before"]:
                    return
                params["before"] = timestamp
                params["offset"] = None

            else:  # offset
                params["offset"] = \
                    text.parse_int(params["offset"]) + params["limit"]
                params["before"] = None
                if params["offset"] >= data["total_posts"]:
                    return

    def _pagination_blogs(self, endpoint, params=None):
        if params is None:
            params = {}
        if self.api_key:
            params["api_key"] = self.api_key
        params["limit"] = 20
        params["offset"] = text.parse_int(params.get("offset"), 0)

        while True:
            data = self._call(endpoint, params)

            blogs = data["blogs"]
            yield from blogs

            params["offset"] = params["offset"] + params["limit"]
            if params["offset"] >= data["total_blogs"]:
                return
