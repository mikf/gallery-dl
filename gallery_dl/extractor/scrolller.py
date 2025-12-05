# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
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
    filename_fmt = "{id}{num:?_//>03}{title:? //[:230]}.{extension}"
    archive_fmt = "{id}_{num}"
    request_interval = (0.5, 1.5)

    def _init(self):
        self.auth_token = None

    def items(self):
        self.login()

        for post in self.posts():
            files = self._extract_files(post)
            post["count"] = len(files)

            yield Message.Directory, "", post
            for file in files:
                url = file["url"]
                post.update(file)
                yield Message.Url, url, text.nameext_from_url(url, post)

    def posts(self):
        return ()

    def _extract_files(self, post):
        album = post.pop("albumContent", None)
        if not album:
            sources = post.get("mediaSources")
            if not sources:
                self.log.warning("%s: No media files", post.get("id"))
                return ()
            src = max(sources, key=self._sort_key)
            src["num"] = 0
            return (src,)

        files = []
        for num, media in enumerate(album, 1):
            sources = media.get("mediaSources")
            if not sources:
                self.log.warning("%s/%s: Missing media file",
                                 post.get("id"), num)
                continue
            src = max(sources, key=self._sort_key)
            src["num"] = num
            files.append(src)
        return files

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
            data = self._request_graphql("LoginQuery", variables, False)
        except exception.HttpError as exc:
            if exc.status == 403:
                raise exception.AuthenticationError()
            raise

        return data["login"]["token"]

    def _request_graphql(self, opname, variables, admin=True):
        headers = {
            "Content-Type"  : None,
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

        if admin:
            url = "https://api.scrolller.com/admin"
            headers["Content-Type"] = "application/json"
        else:
            url = "https://api.scrolller.com/api/v2/graphql"
            headers["Content-Type"] = "text/plain;charset=UTF-8"

        return self.request_json(
            url, method="POST", headers=headers, data=util.json_dumps(data),
        )["data"]

    def _pagination(self, opname, variables, data=None):
        if data is None or not data.get("items"):
            data = self._request_graphql(opname, variables)

        while True:
            while "items" not in data:
                data = data.popitem()[1]
            yield from data["items"]

            if not data["iterator"]:
                return
            variables["iterator"] = data["iterator"]

            data = self._request_graphql(opname, variables)

    def _sort_key(self, src):
        return src["width"], not src["isOptimized"]


class ScrolllerSubredditExtractor(ScrolllerExtractor):
    """Extractor for media from a scrolller subreddit"""
    subcategory = "subreddit"
    pattern = rf"{BASE_PATTERN}(/r/[^/?#]+)(?:/?\?([^#]+))?"
    example = "https://scrolller.com/r/SUBREDDIT"

    def posts(self):
        url, query = self.groups
        filter = None
        sort = "RANDOM"

        if query:
            params = text.parse_query(query)
            if "filter" in params:
                filter = params["filter"].upper().rstrip("S")

        variables = {
            "url"   : url,
            "filter": filter,
            "sortBy": sort,
            "limit" : 50,
        }
        subreddit = self._request_graphql(
            "SubredditQuery", variables)["getSubreddit"]

        variables = {
            "subredditId": subreddit["id"],
            "iterator": None,
            "filter"  : filter,
            "sortBy"  : sort,
            "limit"   : 50,
            "isNsfw"  : subreddit["isNsfw"],
        }
        return self._pagination(
            "SubredditChildrenQuery", variables, subreddit["children"])


class ScrolllerFollowingExtractor(ScrolllerExtractor):
    """Extractor for followed scrolller subreddits"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/following"
    example = "https://scrolller.com/following"

    def items(self):
        self.login()

        if not self.auth_token:
            raise exception.AuthorizationError("Login required")

        variables = {
            "iterator": None,
            "filter"  : None,
            "limit"   : 10,
            "isNsfw"  : False,
            "sortBy"  : "RANDOM",
        }

        for subreddit in self._pagination("GetFollowingSubreddits", variables):
            url = self.root + subreddit["url"]
            subreddit["_extractor"] = ScrolllerSubredditExtractor
            yield Message.Queue, url, subreddit


class ScrolllerPostExtractor(ScrolllerExtractor):
    """Extractor for media from a single scrolller post"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?!r/|following$)([^/?#]+)"
    example = "https://scrolller.com/TITLE-SLUG-a1b2c3d4f5"

    def posts(self):
        variables = {"url": "/" + self.groups[0]}
        data = self._request_graphql("SubredditPostQuery", variables)
        return (data["getPost"],)


QUERIES = {

    "SubredditPostQuery": """\
query SubredditPostQuery(
    $url: String!
) {
    getPost(
        data: { url: $url }
    ) {
        __typename id url title subredditId subredditTitle subredditUrl
        redditPath isNsfw hasAudio fullLengthSource gfycatSource redgifsSource
        ownerAvatar username displayName favoriteCount isPaid tags
        commentsCount commentsRepliesCount isFavorite
        albumContent { mediaSources { url width height isOptimized } }
        mediaSources { url width height isOptimized }
        blurredMediaSources { url width height isOptimized }
    }
}
""",

    "SubredditQuery": """\
query SubredditQuery(
    $url: String!
    $iterator: String
    $sortBy: GallerySortBy
    $filter: GalleryFilter
    $limit: Int!
) {
    getSubreddit(
        data: {
            url: $url,
            iterator: $iterator,
            filter: $filter,
            limit: $limit,
            sortBy: $sortBy
        }
    ) {
        __typename id url title secondaryTitle description createdAt isNsfw
        subscribers isComplete itemCount videoCount pictureCount albumCount
        isPaid username tags isFollowing
        banner { url width height isOptimized }
        children {
            iterator items {
                __typename id url title subredditId subredditTitle subredditUrl
                redditPath isNsfw hasAudio fullLengthSource gfycatSource
                redgifsSource ownerAvatar username displayName favoriteCount
                isPaid tags commentsCount commentsRepliesCount isFavorite
                albumContent { mediaSources { url width height isOptimized } }
                mediaSources { url width height isOptimized }
                blurredMediaSources { url width height isOptimized }
            }
        }
    }
}
""",

    "SubredditChildrenQuery": """\
query SubredditChildrenQuery(
    $subredditId: Int!
    $iterator: String
    $filter: GalleryFilter
    $sortBy: GallerySortBy
    $limit: Int!
    $isNsfw: Boolean
) {
    getSubredditChildren(
        data: {
            subredditId: $subredditId,
            iterator: $iterator,
            filter: $filter,
            sortBy: $sortBy,
            limit: $limit,
            isNsfw: $isNsfw
        },
    ) {
        iterator items {
            __typename id url title subredditId subredditTitle subredditUrl
            redditPath isNsfw hasAudio fullLengthSource gfycatSource
            redgifsSource ownerAvatar username displayName favoriteCount isPaid
            tags commentsCount commentsRepliesCount isFavorite
            albumContent { mediaSources { url width height isOptimized } }
            mediaSources { url width height isOptimized }
            blurredMediaSources { url width height isOptimized }
        }
    }
}
""",

    "GetFollowingSubreddits": """\
query GetFollowingSubreddits(
    $iterator: String,
    $limit: Int!,
    $filter: GalleryFilter,
    $isNsfw: Boolean,
    $sortBy: GallerySortBy
) {
    getFollowingSubreddits(
        data: {
            isNsfw: $isNsfw
            limit: $limit
            filter: $filter
            iterator: $iterator
            sortBy: $sortBy
        }
    ) {
        iterator items {
            __typename id url title secondaryTitle description createdAt isNsfw
            subscribers isComplete itemCount videoCount pictureCount albumCount
            isFollowing
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

    "ItemTypeQuery": """\
query ItemTypeQuery(
    $url: String!
) {
    getItemType(
        url: $url
    )
}
""",

}
