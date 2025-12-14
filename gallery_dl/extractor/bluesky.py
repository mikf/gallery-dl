# -*- coding: utf-8 -*-

# Copyright 2024-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bsky.app/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache, memcache

BASE_PATTERN = (r"(?:https?://)?"
                r"(?:(?:www\.)?(?:c|[fv]x)?bs[ky]y[ex]?\.app|main\.bsky\.dev)")
USER_PATTERN = rf"{BASE_PATTERN}/profile/([^/?#]+)"


class BlueskyExtractor(Extractor):
    """Base class for bluesky extractors"""
    category = "bluesky"
    directory_fmt = ("{category}", "{author[handle]}")
    filename_fmt = "{createdAt[:19]}_{post_id}_{num}.{extension}"
    archive_fmt = "{filename}"
    root = "https://bsky.app"

    def _init(self):
        if meta := self.config("metadata") or ():
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
            elif "item" in post:
                post = post["item"]
            if self._user_did and post["author"]["did"] != self._user_did:
                self.log.debug("Skipping %s (repost)", self._pid(post))
                continue
            embed = post.get("embed")
            try:
                post.update(post.pop("record"))
            except Exception:
                self.log.debug("Skipping %s (no 'record')", self._pid(post))
                continue

            while True:
                self._prepare(post)
                files = self._extract_files(post)

                yield Message.Directory, "", post
                if files:
                    did = post["author"]["did"]
                    base = (f"{self.api.service_endpoint(did)}/xrpc"
                            f"/com.atproto.sync.getBlob?did={did}&cid=")
                    for post["num"], file in enumerate(files, 1):
                        post.update(file)
                        yield Message.Url, base + file["filename"], post

                if not self.quoted or not embed or "record" not in embed:
                    break

                quote = embed["record"]
                if "record" in quote:
                    quote = quote["record"]
                value = quote.pop("value", None)
                if value is None:
                    break
                quote["quote_id"] = self._pid(post)
                quote["quote_by"] = post["author"]
                embed = quote.get("embed")
                quote.update(value)
                post = quote

    def posts(self):
        return ()

    def _posts_records(self, actor, collection):
        depth = self.config("depth", "0")

        for record in self.api.list_records(actor, collection):
            uri = None
            try:
                uri = record["value"]["subject"]["uri"]
                if "/app.bsky.feed.post/" in uri:
                    yield from self.api.get_post_thread_uri(uri, depth)
            except exception.ControlException:
                pass  # deleted post
            except Exception as exc:
                self.log.debug(record, exc_info=exc)
                self.log.warning("Failed to extract %s (%s: %s)",
                                 uri or "record", exc.__class__.__name__, exc)

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
        post["date"] = self.parse_datetime_iso(post["createdAt"][:19])

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
                try:
                    files.append(self._extract_media(image, "image"))
                except Exception:
                    pass
        if "video" in media and self.videos:
            try:
                files.append(self._extract_media(media, "video"))
            except Exception:
                pass

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


class BlueskyUserExtractor(Dispatch, BlueskyExtractor):
    pattern = rf"{USER_PATTERN}$"
    example = "https://bsky.app/profile/HANDLE"

    def items(self):
        base = f"{self.root}/profile/{self.groups[0]}/"
        default = ("posts" if self.config("quoted", False) or
                   self.config("reposts", False) else "media")
        return self._dispatch_extractors((
            (BlueskyInfoExtractor      , base + "info"),
            (BlueskyAvatarExtractor    , base + "avatar"),
            (BlueskyBackgroundExtractor, base + "banner"),
            (BlueskyPostsExtractor     , base + "posts"),
            (BlueskyRepliesExtractor   , base + "replies"),
            (BlueskyMediaExtractor     , base + "media"),
            (BlueskyVideoExtractor     , base + "video"),
            (BlueskyLikesExtractor     , base + "likes"),
        ), (default,))


class BlueskyPostsExtractor(BlueskyExtractor):
    subcategory = "posts"
    pattern = rf"{USER_PATTERN}/posts"
    example = "https://bsky.app/profile/HANDLE/posts"

    def posts(self):
        return self.api.get_author_feed(
            self.groups[0], "posts_and_author_threads")


class BlueskyRepliesExtractor(BlueskyExtractor):
    subcategory = "replies"
    pattern = rf"{USER_PATTERN}/replies"
    example = "https://bsky.app/profile/HANDLE/replies"

    def posts(self):
        return self.api.get_author_feed(
            self.groups[0], "posts_with_replies")


class BlueskyMediaExtractor(BlueskyExtractor):
    subcategory = "media"
    pattern = rf"{USER_PATTERN}/media"
    example = "https://bsky.app/profile/HANDLE/media"

    def posts(self):
        return self.api.get_author_feed(
            self.groups[0], "posts_with_media")


class BlueskyVideoExtractor(BlueskyExtractor):
    subcategory = "video"
    pattern = rf"{USER_PATTERN}/video"
    example = "https://bsky.app/profile/HANDLE/video"

    def posts(self):
        return self.api.get_author_feed(
            self.groups[0], "posts_with_video")


class BlueskyLikesExtractor(BlueskyExtractor):
    subcategory = "likes"
    pattern = rf"{USER_PATTERN}/likes"
    example = "https://bsky.app/profile/HANDLE/likes"

    def posts(self):
        if self.config("endpoint") == "getActorLikes":
            return self.api.get_actor_likes(self.groups[0])
        return self._posts_records(self.groups[0], "app.bsky.feed.like")


class BlueskyFeedExtractor(BlueskyExtractor):
    subcategory = "feed"
    pattern = rf"{USER_PATTERN}/feed/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/feed/NAME"

    def posts(self):
        actor, feed = self.groups
        return self.api.get_feed(actor, feed)


class BlueskyListExtractor(BlueskyExtractor):
    subcategory = "list"
    pattern = rf"{USER_PATTERN}/lists/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/lists/ID"

    def posts(self):
        actor, list_id = self.groups
        return self.api.get_list_feed(actor, list_id)


class BlueskyFollowingExtractor(BlueskyExtractor):
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/follows"
    example = "https://bsky.app/profile/HANDLE/follows"

    def items(self):
        for user in self.api.get_follows(self.groups[0]):
            url = "https://bsky.app/profile/" + user["did"]
            user["_extractor"] = BlueskyUserExtractor
            yield Message.Queue, url, user


class BlueskyPostExtractor(BlueskyExtractor):
    subcategory = "post"
    pattern = rf"{USER_PATTERN}/post/([^/?#]+)"
    example = "https://bsky.app/profile/HANDLE/post/ID"

    def posts(self):
        actor, post_id = self.groups
        return self.api.get_post_thread(actor, post_id)


class BlueskyInfoExtractor(BlueskyExtractor):
    subcategory = "info"
    pattern = rf"{USER_PATTERN}/info"
    example = "https://bsky.app/profile/HANDLE/info"

    def items(self):
        self._metadata_user = True
        self.api._did_from_actor(self.groups[0])
        return iter(((Message.Directory, "", self._user),))


class BlueskyAvatarExtractor(BlueskyExtractor):
    subcategory = "avatar"
    filename_fmt = "avatar_{post_id}.{extension}"
    pattern = rf"{USER_PATTERN}/avatar"
    example = "https://bsky.app/profile/HANDLE/avatar"

    def posts(self):
        return self._make_post(self.groups[0], "avatar")


class BlueskyBackgroundExtractor(BlueskyExtractor):
    subcategory = "background"
    filename_fmt = "background_{post_id}.{extension}"
    pattern = rf"{USER_PATTERN}/ba(?:nner|ckground)"
    example = "https://bsky.app/profile/HANDLE/banner"

    def posts(self):
        return self._make_post(self.groups[0], "banner")


class BlueskySearchExtractor(BlueskyExtractor):
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search(?:/|\?q=)(.+)"
    example = "https://bsky.app/search?q=QUERY"

    def posts(self):
        query = text.unquote(self.groups[0].replace("+", " "))
        return self.api.search_posts(query)


class BlueskyHashtagExtractor(BlueskyExtractor):
    subcategory = "hashtag"
    pattern = rf"{BASE_PATTERN}/hashtag/([^/?#]+)(?:/(top|latest))?"
    example = "https://bsky.app/hashtag/NAME"

    def posts(self):
        hashtag, order = self.groups
        return self.api.search_posts("#"+hashtag, order)


class BlueskyBookmarkExtractor(BlueskyExtractor):
    subcategory = "bookmark"
    pattern = rf"{BASE_PATTERN}/saved"
    example = "https://bsky.app/saved"

    def posts(self):
        return self.api.get_bookmarks()


class BlueskyAPI():
    """Interface for the Bluesky API

    https://docs.bsky.app/docs/category/http-reference
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.headers = {"Accept": "application/json"}

        self.username, self.password = extractor._get_auth_info()
        if srv := extractor.config("api-server", False):
            self.root = srv.rstrip("/")
        elif self.username:
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
        return self._pagination(endpoint, params, check_empty=True)

    def get_author_feed(self, actor, filter="posts_and_author_threads"):
        endpoint = "app.bsky.feed.getAuthorFeed"
        params = {
            "actor" : self._did_from_actor(actor, True),
            "filter": filter,
            "limit" : "100",
        }
        return self._pagination(endpoint, params)

    def get_bookmarks(self):
        endpoint = "app.bsky.bookmark.getBookmarks"
        return self._pagination(endpoint, {}, "bookmarks", check_empty=True)

    def get_feed(self, actor, feed):
        endpoint = "app.bsky.feed.getFeed"
        uri = (f"at://{self._did_from_actor(actor)}"
               f"/app.bsky.feed.generator/{feed}")
        params = {"feed": uri, "limit": "100"}
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
        uri = f"at://{self._did_from_actor(actor)}/app.bsky.graph.list/{list}"
        params = {"list" : uri, "limit": "100"}
        return self._pagination(endpoint, params)

    def get_post_thread(self, actor, post_id):
        uri = (f"at://{self._did_from_actor(actor)}"
               f"/app.bsky.feed.post/{post_id}")
        depth = self.extractor.config("depth", "0")
        return self.get_post_thread_uri(uri, depth)

    def get_post_thread_uri(self, uri, depth="0"):
        endpoint = "app.bsky.feed.getPostThread"
        params = {
            "uri"         : uri,
            "depth"       : depth,
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

    def list_records(self, actor, collection):
        endpoint = "com.atproto.repo.listRecords"
        actor_did = self._did_from_actor(actor)
        params = {
            "repo"      : actor_did,
            "collection": collection,
            "limit"     : "100",
            #  "reverse"   : "false",
        }
        return self._pagination(endpoint, params, "records",
                                self.service_endpoint(actor_did))

    @memcache(keyarg=1)
    def resolve_handle(self, handle):
        endpoint = "com.atproto.identity.resolveHandle"
        params = {"handle": handle}
        return self._call(endpoint, params)["did"]

    @memcache(keyarg=1)
    def service_endpoint(self, did):
        if did.startswith('did:web:'):
            url = "https://" + did[8:] + "/.well-known/did.json"
        else:
            url = "https://plc.directory/" + did

        try:
            data = self.extractor.request_json(url)
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

        url = f"{self.root}/xrpc/{endpoint}"
        response = self.extractor.request(
            url, method="POST", headers=headers, json=data, fatal=None)
        data = response.json()

        if response.status_code != 200:
            self.log.debug("Server response: %s", data)
            raise exception.AuthenticationError(
                f"\"{data.get('error')}: {data.get('message')}\"")

        _refresh_token_cache.update(self.username, data["refreshJwt"])
        return "Bearer " + data["accessJwt"]

    def _call(self, endpoint, params, root=None):
        if root is None:
            root = self.root
        url = f"{root}/xrpc/{endpoint}"

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

            msg = "API request failed"
            try:
                data = response.json()
                msg = f"{msg} ('{data['error']}: {data['message']}')"
            except Exception:
                msg = f"{msg} ({response.status_code} {response.reason})"

            self.extractor.log.debug("Server response: %s", response.text)
            raise exception.AbortExtraction(msg)

    def _pagination(self, endpoint, params,
                    key="feed", root=None, check_empty=False):
        while True:
            data = self._call(endpoint, params, root)

            if check_empty and not data[key]:
                return
            yield from data[key]

            cursor = data.get("cursor")
            if not cursor:
                return
            params["cursor"] = cursor


@cache(maxage=84*86400, keyarg=0)
def _refresh_token_cache(username):
    return None
