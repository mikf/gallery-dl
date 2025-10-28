# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text


class KemonoAPI():
    """Interface for the Kemono API v1.3.0

    https://kemono.cr/documentation/api
    """

    def __init__(self, extractor):
        self.extractor = extractor
        self.root = f"{extractor.root}/api"
        self.headers = {"Accept": "text/css"}

    def posts(self, offset=0, query=None, tags=None):
        endpoint = "/v1/posts"
        params = {"q": query, "o": offset, "tag": tags}
        return self._pagination(endpoint, params, 50, "posts")

    def file(self, file_hash):
        endpoint = f"/v1/file/{file_hash}"
        return self._call(endpoint)

    def creators(self):
        endpoint = "/v1/creators"
        return self._call(endpoint)

    def creator_posts(self, service, creator_id,
                      offset=0, query=None, tags=None):
        endpoint = f"/v1/{service}/user/{creator_id}/posts"
        params = {"o": offset, "tag": tags, "q": query}
        return self._pagination(endpoint, params, 50)

    def creator_posts_expand(self, service, creator_id,
                             offset=0, query=None, tags=None):
        for post in self.creator_posts(
                service, creator_id, offset, query, tags):
            yield self.creator_post(
                service, creator_id, post["id"])["post"]

    def creator_announcements(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/announcements"
        return self._call(endpoint)

    def creator_dms(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/dms"
        return self._call(endpoint)

    def creator_fancards(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/fancards"
        return self._call(endpoint)

    def creator_post(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}"
        return self._call(endpoint)

    def creator_post_comments(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/comments"
        return self._call(endpoint, fatal=False)

    def creator_post_revisions(self, service, creator_id, post_id):
        endpoint = f"/v1/{service}/user/{creator_id}/post/{post_id}/revisions"
        return self._call(endpoint, fatal=False)

    def creator_profile(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/profile"
        return self._call(endpoint)

    def creator_links(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/links"
        return self._call(endpoint)

    def creator_tags(self, service, creator_id):
        endpoint = f"/v1/{service}/user/{creator_id}/tags"
        return self._call(endpoint)

    def discord_channel(self, channel_id, post_count=None):
        endpoint = f"/v1/discord/channel/{channel_id}"
        if post_count is None:
            return self._pagination(endpoint, {}, 150)
        else:
            return self._pagination_reverse(endpoint, {}, 150, post_count)

    def discord_channel_lookup(self, server_id):
        endpoint = f"/v1/discord/channel/lookup/{server_id}"
        return self._call(endpoint)

    def discord_server(self, server_id):
        endpoint = f"/v1/discord/server/{server_id}"
        return self._call(endpoint)

    def account_favorites(self, type):
        endpoint = "/v1/account/favorites"
        params = {"type": type}
        return self._call(endpoint, params)

    def _call(self, endpoint, params=None, headers=None, fatal=True):
        if headers is None:
            headers = self.headers
        else:
            headers = {**self.headers, **headers}

        return self.extractor.request_json(
            f"{self.root}{endpoint}", params=params, headers=headers,
            encoding="utf-8", fatal=fatal)

    def _pagination(self, endpoint, params, batch=50, key=None):
        offset = text.parse_int(params.get("o"))
        params["o"] = offset - offset % batch

        while True:
            data = self._call(endpoint, params)

            if key is not None:
                data = data.get(key)
            if not data:
                return
            yield from data

            if len(data) < batch:
                return
            params["o"] += batch

    def _pagination_reverse(self, endpoint, params, batch, count):
        params["o"] = count // batch * batch

        while True:
            data = self._call(endpoint, params)

            if not data:
                return
            data.reverse()
            yield from data

            if not params["o"]:
                return
            params["o"] -= batch
