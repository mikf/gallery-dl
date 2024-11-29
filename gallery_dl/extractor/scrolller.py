# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://scrolller.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?scrolller\.com"


class ScrolllerExtractor(Extractor):
    """Base class for scrolller extractors"""
    category = "scrolller"
    root = "https://scrolller.com"
    directory_fmt = ("{category}", "{subredditTitle}")
    filename_fmt = "{id}{title:? //}.{extension}"
    archive_fmt = "{id}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.auth_token = None

    def items(self):
        self.login()

        for post in self.posts():

            media_sources = post.get("mediaSources")
            if not media_sources:
                self.log.warning("%s: No media files", post.get("id"))
                continue

            src = max(media_sources, key=self._sort_key)
            post.update(src)
            url = src["url"]
            text.nameext_from_url(url, post)

            yield Message.Directory, post
            yield Message.Url, url, post

    def posts(self):
        return ()

    def login(self):
        username, password = self._get_auth_info()
        if username:
            self.auth_token = self._login_impl(username, password)

    @cache(maxage=28*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        variables = {
            "username": username,
            "password": password,
        }

        try:
            data = self._request_graphql("LoginQuery", variables)
        except exception.HttpError as exc:
            if exc.status == 403:
                raise exception.AuthenticationError()
            raise

        return data["login"]["token"]

    def _request_graphql(self, opname, variables):
        url = "https://api.scrolller.com/api/v2/graphql"
        headers = {
            "Content-Type"  : "text/plain;charset=UTF-8",
            "Origin"        : self.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        data = {
            "query"        : QUERIES[opname],
            "variables"    : variables,
            "authorization": self.auth_token,
        }
        return self.request(
            url, method="POST", headers=headers, data=util.json_dumps(data),
        ).json()["data"]

    def _pagination(self, opname, variables):
        while True:
            data = self._request_graphql(opname, variables)

            while "items" not in data:
                data = data.popitem()[1]
            yield from data["items"]

            if not data["iterator"]:
                return
            variables["iterator"] = data["iterator"]

    def _sort_key(self, src):
        return src["width"], not src["isOptimized"]


class ScrolllerSubredditExtractor(ScrolllerExtractor):
    """Extractor for media from a scrolller subreddit"""
    subcategory = "subreddit"
    pattern = BASE_PATTERN + r"(/r/[^/?#]+)(?:/?\?([^#]+))?"
    example = "https://scrolller.com/r/SUBREDDIT"

    def posts(self):
        url, query = self.groups
        filter = None

        if query:
            params = text.parse_query(query)
            if "filter" in params:
                filter = params["filter"].upper().rstrip("S")

        variables = {
            "url"      : url,
            "iterator" : None,
            "filter"   : filter,
            "hostsDown": None,
        }
        return self._pagination("SubredditQuery", variables)


class ScrolllerFollowingExtractor(ScrolllerExtractor):
    """Extractor for followed scrolller subreddits"""
    subcategory = "following"
    pattern = BASE_PATTERN + r"/following"
    example = "https://scrolller.com/following"

    def items(self):
        self.login()

        if not self.auth_token:
            raise exception.AuthorizationError("Login required")

        variables = {
            "iterator" : None,
            "hostsDown": None,
        }

        for subreddit in self._pagination("FollowingQuery", variables):
            url = self.root + subreddit["url"]
            subreddit["_extractor"] = ScrolllerSubredditExtractor
            yield Message.Queue, url, subreddit


class ScrolllerPostExtractor(ScrolllerExtractor):
    """Extractor for media from a single scrolller post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?!r/|following$)([^/?#]+)"
    example = "https://scrolller.com/title-slug-a1b2c3d4f5"

    def posts(self):
        url = "{}/{}".format(self.root, self.groups[0])
        page = self.request(url).text
        data = util.json_loads(text.extr(
            page, '<script>window.scrolllerConfig="', '"</script>')
            .replace('\\"', '"'))
        return (data["item"],)


QUERIES = {

    "SubredditQuery": """\
query SubredditQuery(
    $url: String!
    $filter: SubredditPostFilter
    $iterator: String
) {
    getSubreddit(
        url: $url
    ) {
        children(
            limit: 50
            iterator: $iterator
            filter: $filter
            disabledHosts: null
        ) {
            iterator items {
                __typename id url title subredditId subredditTitle
                subredditUrl redditPath isNsfw albumUrl hasAudio
                fullLengthSource gfycatSource redgifsSource ownerAvatar
                username displayName isPaid tags isFavorite
                mediaSources { url width height isOptimized }
                blurredMediaSources { url width height isOptimized }
            }
        }
    }
}
""",

    "FollowingQuery": """\
query FollowingQuery(
    $iterator: String
) {
    getFollowing(
        limit: 10
        iterator: $iterator
    ) {
        iterator items {
            __typename id url title secondaryTitle description createdAt isNsfw
            subscribers isComplete itemCount videoCount pictureCount albumCount
            isPaid username tags isFollowing
            banner { url width height isOptimized }
        }
    }
}
""",

    "LoginQuery": """\
query LoginQuery(
    $username: String!,
    $password: String!
) {
    login(
        username: $username,
        password: $password
    ) {
        username token expiresAt isAdmin status isPremium
    }
}
""",

}
