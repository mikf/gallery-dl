# -*- coding: utf-8 -*-

# Copyright 2024 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bsky.app/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache

BASE_PATTERN = (r"(?:https?://)?"
                r"(?:(?:www\.)?(?:c|[fv]x)?bs[ky]y[ex]?\.app|main\.bsky\.dev)")
USER_PATTERN = BASE_PATTERN + r"/profile/([^/?#]+)"


class BlueskyExtractor(Extractor):
    """Base class for bluesky extractors"""
    category = "bluesky"
    directory_fmt = ("{category}", "{author[handle]}")
    filename_fmt = "{createdAt[:19]}_{post_id}_{num}.{extension}"
    archive_fmt = "{filename}"
    root = "https://bsky.app"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user = match.group(1)

    def _init(self):
        meta = self.config("metadata") or ()
        if meta:
            if isinstance(meta, str):
                meta = meta.replace(" ", "").split(",")
            elif not isinstance(meta, (list, tuple)):
                meta = ("user", "facets")
        self._metadata_user = ("user" in meta)
        self._metadata_facets = ("facets" in meta)

        self.api = BlueskyAPI(self)
        self._user = self._user_did = None
        self.instance = self.root.partition("://")[2]
        self.videos = self.config("videos", True)
        self.quoted = self.config("quoted", False)

    def items(self):
        for post in self.posts():
            if "post" in post:
                post = post["post"]
            if self._user_did and post["author"]["did"] != self._user_did:
                self.log.debug("Skipping %s (repost)", self._pid(post))
                continue
            embed = post.get("embed")
            post.update(post.pop("record"))

            while True:
                self._prepare(post)
                files = self._extract_files(post)

                yield Message.Directory, post
                if files:
                    did = post["author"]["did"]
                    base = (
                        "{}/xrpc/com.atproto.sync.getBlob?did={}&cid=".format(
                            self.api.get_service_endpoint(did), did))
                    for post["num"], file in enumerate(files, 1):
                        post.update(file)
                        yield Message.Url, base + file["filename"], post

                if not self.quoted or not embed or "record" not in embed:
                    break

                quote = embed["record"]
                if "record" in quote:
                    quote = quote["record"]
                quote["quote_id"] = self._pid(post)
                quote["quote_by"] = post["author"]
                embed = quote.get("embed")
                quote.update(quote.pop("value"))
                post = quote

    def posts(self):
        return ()

    def _pid(self, post):
        return post["uri"].rpartition("/")[2]

    @memcache(keyarg=1)
    def _instance(self, handle):
        return ".".join(handle.rsplit(".", 2)[-2:])

    def _prepare(self, post):
        author = post["author"]
        author["instance"] = self._instance(author["handle"])

        if self._metadata_facets:
            if "facets" in post:
                post["hashtags"] = tags = []
                post["mentions"] = dids = []
                post["uris"] = uris = []
                for facet in post["facets"]:
                    features = facet["features"][0]
                    if "tag" in features:
                        tags.append(features["tag"])
                    elif "did" in features:
                        dids.append(features["did"])
                    elif "uri" in features:
                        uris.append(features["uri"])
            else:
                post["hashtags"] = post["mentions"] = post["uris"] = ()

        if self._metadata_user:
            post["user"] = self._user or author

        post["instance"] = self.instance
        post["post_id"] = self._pid(post)
        post["date"] = text.parse_datetime(
            post["createdAt"][:19], "%Y-%m-%dT%H:%M:%S")

    def _extract_files(self, post):
        if "embed" not in post:
            post["count"] = 0
            return ()

        files = []
        media = post["embed"]
        if "media" in media:
            media = media["media"]

        if "images" in media:
            for image in media["images"]:
                files.append(self._extract_media(image, "image"))
        if "video" in media and self.videos:
            files.append(self._extract_media(media, "video"))

        post["count"] = len(files)
        return files

    def _extract_media(self, media, key):
        try:
            aspect = media["aspectRatio"]
            width = aspect["width"]
            height = aspect["height"]
        except KeyError:
            width = height = 0

        data = media[key]
        try:
            cid = data["ref"]["$link"]
        except KeyError:
            cid = data["cid"]

        return {
            "description": media.get("alt") or "",
            "width"      : width,
            "height"     : height,
            "filename"   : cid,
            "extension"  : data["mimeType"].rpartition("/")[2],
        }

    def _make_post(self, actor, kind):
        did = self.api._did_from_actor(actor)
        profile = self.api.get_profile(did)

        if kind not in profile:
            return ()
        cid = profile[kind].rpartition("/")[2].partition("@")[0]

        return ({
            "post": {
                "embed": {"images": [{
                    "alt": kind,
                    "image": {
                        "$type"   : "blob",
                        "ref"     : {"$link": cid},
                        "mimeType": "image/jpeg",
                        "size"    : 0,
                    },
                    "aspectRatio": {
                        "width" : 1000,
                        "height": 1000,
                    },
                }]},
                "author"   : profile,
                "record"   : (),
                "createdAt": "",
                "uri"      : cid,
            },
        },)


class BlueskyUserExtractor(BlueskyExtractor):
    subcategory = "user"
    pattern = USER_PATTERN + r"$"
    example = "https://bsky.app/profile/HANDLE"

    def initialize(self):
        pass

    def items(self):
        base = "{}/profile/{}/".format(self.root, self.user)
        return self._dispatch_extractors((
            (BlueskyAvatarExtractor    , base + "avatar"),
            (BlueskyBackgroundExtractor, base + "banner"),
            (BlueskyPostsExtractor     , base + "posts"),
            (BlueskyRepliesExtractor   , base + "replies"),
            (BlueskyMediaExtractor     , base + "media"),
            (BlueskyLikesExtractor     , base + "likes"),
        ), ("media",))


class BlueskyPostsExtractor(BlueskyExtractor):
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    example = "https://bsky.app/profile/HANDLE/posts"

    def posts(self):
        return self.api.get_author_feed(self.user, "posts_and_author_threads")


class BlueskyRepliesExtractor(BlueskyExtractor):
    subcategory = "replies"
    pattern = USER_PATTERN + r"/replies"
    example = "https://bsky.app/profile/HANDLE/replies"

    def posts(self):
        return self.api.get_author_feed(self.user, "posts_with_replies")


class BlueskyMediaExtractor(BlueskyExtractor):
    subcategory = "media"
    pattern = USER_PATTERN + r"/media"
    example = "https://bsky.app/profile/HANDLE/media"

    def posts(self):
        return self.api.get_author_feed(self.user, "posts_with_media")


class BlueskyLikesExtractor(BlueskyExtractor):
    subcategory = "likes"
    pattern = USER_PATTERN + r"/likes"
    example = "https://bsky.app/profile/HANDLE/likes"

    def posts(self):
        return self.api.get_actor_likes(self.user)


class BlueskyFeedExtractor(BlueskyExtractor):
    subcategory = "feed"
    pattern = USER_PATTERN + r"/feed/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/feed/NAME"

    def __init__(self, match):
        BlueskyExtractor.__init__(self, match)
        self.feed = match.group(2)

    def posts(self):
        return self.api.get_feed(self.user, self.feed)


class BlueskyListExtractor(BlueskyExtractor):
    subcategory = "list"
    pattern = USER_PATTERN + r"/lists/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/lists/ID"

    def __init__(self, match):
        BlueskyExtractor.__init__(self, match)
        self.list = match.group(2)

    def posts(self):
        return self.api.get_list_feed(self.user, self.list)


class BlueskyFollowingExtractor(BlueskyExtractor):
    subcategory = "following"
    pattern = USER_PATTERN + r"/follows"
    example = "https://bsky.app/profile/HANDLE/follows"

    def items(self):
        for user in self.api.get_follows(self.user):
            url = "https://bsky.app/profile/" + user["did"]
            user["_extractor"] = BlueskyUserExtractor
            yield Message.Queue, url, user


class BlueskyPostExtractor(BlueskyExtractor):
    subcategory = "post"
    pattern = USER_PATTERN + r"/post/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/post/ID"

    def __init__(self, match):
        BlueskyExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        return self.api.get_post_thread(self.user, self.post_id)


class BlueskyAvatarExtractor(BlueskyExtractor):
    subcategory = "avatar"
    filename_fmt = "avatar_{post_id}.{extension}"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://bsky.app/profile/HANDLE/avatar"

    def posts(self):
        return self._make_post(self.user, "avatar")


class BlueskyBackgroundExtractor(BlueskyExtractor):
    subcategory = "background"
    filename_fmt = "background_{post_id}.{extension}"
    pattern = USER_PATTERN + r"/ba(?:nner|ckground)"
    example = "https://bsky.app/profile/HANDLE/banner"

    def posts(self):
        return self._make_post(self.user, "banner")


class BlueskySearchExtractor(BlueskyExtractor):
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(?:/|\?q=)(.+)"
    example = "https://bsky.app/search?q=QUERY"

    def posts(self):
        return self.api.search_posts(self.user)


class BlueskyHashtagExtractor(BlueskyExtractor):
    subcategory = "hashtag"
    pattern = BASE_PATTERN + r"/hashtag/([^/?#]+)(?:/(top|latest))?"
    example = "https://bsky.app/hashtag/NAME"

    def posts(self):
        return self.api.search_posts("#"+self.user, self.groups[1])


class BlueskyAPI():
    """Interface for the Bluesky API

    https://www.docs.bsky.app/docs/category/http-reference
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {"Accept": "application/json"}

        self.username, self.password = extractor._get_auth_info()
        if self.username:
            self.root = "https://bsky.social"
        else:
            self.root = "https://api.bsky.app"
            self.authenticate = util.noop

    def get_actor_likes(self, actor):
        endpoint = "app.bsky.feed.getActorLikes"
        params = {
            "actor": self._did_from_actor(actor),
            "limit": "100",
        }
        return self._pagination(endpoint, params)

    def get_author_feed(self, actor, filter="posts_and_author_threads"):
        endpoint = "app.bsky.feed.getAuthorFeed"
        params = {
            "actor" : self._did_from_actor(actor, True),
            "filter": filter,
            "limit" : "100",
        }
        return self._pagination(endpoint, params)

    def get_feed(self, actor, feed):
        endpoint = "app.bsky.feed.getFeed"
        params = {
            "feed" : "at://{}/app.bsky.feed.generator/{}".format(
                self._did_from_actor(actor), feed),
            "limit": "100",
        }
        return self._pagination(endpoint, params)

    def get_follows(self, actor):
        endpoint = "app.bsky.graph.getFollows"
        params = {
            "actor": self._did_from_actor(actor),
            "limit": "100",
        }
        return self._pagination(endpoint, params, "follows")

    def get_list_feed(self, actor, list):
        endpoint = "app.bsky.feed.getListFeed"
        params = {
            "list" : "at://{}/app.bsky.graph.list/{}".format(
                self._did_from_actor(actor), list),
            "limit": "100",
        }
        return self._pagination(endpoint, params)

    def get_post_thread(self, actor, post_id):
        endpoint = "app.bsky.feed.getPostThread"
        params = {
            "uri": "at://{}/app.bsky.feed.post/{}".format(
                self._did_from_actor(actor), post_id),
            "depth"       : self.extractor.config("depth", "0"),
            "parentHeight": "0",
        }

        thread = self._call(endpoint, params)["thread"]
        if "replies" not in thread:
            return (thread,)

        index = 0
        posts = [thread]
        while index < len(posts):
            post = posts[index]
            if "replies" in post:
                posts.extend(post["replies"])
            index += 1
        return posts

    @memcache(keyarg=1)
    def get_profile(self, did):
        endpoint = "app.bsky.actor.getProfile"
        params = {"actor": did}
        return self._call(endpoint, params)

    @memcache(keyarg=1)
    def resolve_handle(self, handle):
        endpoint = "com.atproto.identity.resolveHandle"
        params = {"handle": handle}
        return self._call(endpoint, params)["did"]

    @memcache(keyarg=1)
    def get_service_endpoint(self, did):
        if did.startswith('did:web:'):
            url = "https://{}/.well-known/did.json".format(
                did.rpartition(":")[2])
        else:
            url = "https://plc.directory/" + did

        try:
            data = self.extractor.request(url).json()
            for service in data["service"]:
                if service["type"] == "AtprotoPersonalDataServer":
                    return service["serviceEndpoint"]
        except Exception:
            pass
        return "https://bsky.social"

    def search_posts(self, query, sort=None):
        endpoint = "app.bsky.feed.searchPosts"
        params = {
            "q"    : query,
            "limit": "100",
            "sort" : sort,
        }
        return self._pagination(endpoint, params, "posts")

    def _did_from_actor(self, actor, user_did=False):
        if actor.startswith("did:"):
            did = actor
        else:
            did = self.resolve_handle(actor)

        extr = self.extractor
        if user_did and not extr.config("reposts", False):
            extr._user_did = did
        if extr._metadata_user:
            extr._user = user = self.get_profile(did)
            user["instance"] = extr._instance(user["handle"])

        return did

    def authenticate(self):
        self.headers["Authorization"] = self._authenticate_impl(self.username)

    @cache(maxage=3600, keyarg=1)
    def _authenticate_impl(self, username):
        refresh_token = _refresh_token_cache(username)

        if refresh_token:
            self.log.info("Refreshing access token for %s", username)
            endpoint = "com.atproto.server.refreshSession"
            headers = {"Authorization": "Bearer " + refresh_token}
            data = None
        else:
            self.log.info("Logging in as %s", username)
            endpoint = "com.atproto.server.createSession"
            headers = None
            data = {
                "identifier": username,
                "password"  : self.password,
            }

        url = "{}/xrpc/{}".format(self.root, endpoint)
        response = self.extractor.request(
            url, method="POST", headers=headers, json=data, fatal=None)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError('"{}: {}"'.format(
                data.get("error"), data.get("message")))

        _refresh_token_cache.update(self.username, data["refreshJwt"])
        return "Bearer " + data["accessJwt"]

    def _call(self, endpoint, params):
        url = "{}/xrpc/{}".format(self.root, endpoint)

        while True:
            self.authenticate()
            response = self.extractor.request(
                url, params=params, headers=self.headers, fatal=None)

            if response.status_code < 400:
                return response.json()
            if response.status_code == 429:
                until = response.headers.get("RateLimit-Reset")
                self.extractor.wait(until=until)
                continue

            try:
                data = response.json()
                msg = "API request failed ('{}: {}')".format(
                    data["error"], data["message"])
            except Exception:
                msg = "API request failed ({} {})".format(
                    response.status_code, response.reason)

            self.extractor.log.debug("Server response: %s", response.text)
            raise exception.StopExtraction(msg)

    def _pagination(self, endpoint, params, key="feed"):
        while True:
            data = self._call(endpoint, params)
            yield from data[key]

            cursor = data.get("cursor")
            if not cursor:
                return
            params["cursor"] = cursor


@cache(maxage=84*86400, keyarg=0)
def _refresh_token_cache(username):
    return None
