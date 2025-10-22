# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import util, exception
from ...cache import cache, memcache


@cache(maxage=84*86400, keyarg=0)
def _refresh_token_cache(username):
    return None


class BlueskyAPI():
    """Interface for the Bluesky API

    https://docs.bsky.app/docs/category/http-reference
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
