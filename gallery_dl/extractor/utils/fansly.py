# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import time


class FanslyAPI():
    ROOT = "https://apiv3.fansly.com"

    def __init__(self, extractor):
        self.extractor = extractor
        self.headers = {
            "fansly-client-ts": None,
            "Origin"          : extractor.root,
        }

        if token := extractor.config("token"):
            self.headers["authorization"] = token
            self.extractor.log.debug(
                "Using authorization 'token' %.5s...", token)
        else:
            self.extractor.log.warning("No 'token' provided")

    def account(self, creator):
        if creator.startswith("id:"):
            return self.account_by_id(creator[3:])
        return self.account_by_username(creator)

    def account_by_username(self, username):
        endpoint = "/v1/account"
        params = {"usernames": username}
        return self._call(endpoint, params)[0]

    def account_by_id(self, account_id):
        endpoint = "/v1/account"
        params = {"ids": account_id}
        return self._call(endpoint, params)[0]

    def accounts_by_id(self, account_ids):
        endpoint = "/v1/account"
        params = {"ids": ",".join(map(str, account_ids))}
        return self._call(endpoint, params)

    def account_media(self, media_ids):
        endpoint = "/v1/account/media"
        params = {"ids": ",".join(map(str, media_ids))}
        return self._call(endpoint, params)

    def lists_account(self):
        endpoint = "/v1/lists/account"
        params = {"itemId": ""}
        return self._call(endpoint, params)

    def lists_itemsnew(self, list_id, sort="3"):
        endpoint = "/v1/lists/itemsnew"
        params = {
            "listId"  : list_id,
            "limit"   : 50,
            "after"   : None,
            "sortMode": sort,
        }
        return self._pagination_list(endpoint, params)

    def mediaoffers_location(self, account_id, wall_id):
        endpoint = "/v1/mediaoffers/location"
        params = {
            "locationId": wall_id,
            "locationType": "1002",
            "accountId": account_id,
            "mediaType": "",
            "before": "",
            "after" : "0",
            "limit" : "30",
            "offset": "0",
        }
        return self._pagination_media(endpoint, params)

    def post(self, post_id):
        endpoint = "/v1/post"
        params = {"ids": post_id}
        return self._update_posts(self._call(endpoint, params))

    def timeline_home(self, mode="0", list_id=None):
        endpoint = "/v1/timeline/home"
        params = {"before": "0", "after": "0"}
        if list_id is None:
            params["mode"] = mode
        else:
            params["listId"] = list_id
        return self._pagination(endpoint, params)

    def timeline_new(self, account_id, wall_id):
        endpoint = f"/v1/timelinenew/{account_id}"
        params = {
            "before"       : "0",
            "after"        : "0",
            "wallId"       : wall_id,
            "contentSearch": "",
        }
        return self._pagination(endpoint, params)

    def _update_posts(self, response):
        accounts = {
            account["id"]: account
            for account in response["accounts"]
        }
        media = {
            media["id"]: media
            for media in response["accountMedia"]
        }
        bundles = {
            bundle["id"]: bundle
            for bundle in response["accountMediaBundles"]
        }

        posts = response["posts"]
        for post in posts:
            post["account"] = accounts[post.pop("accountId")]

            extra = None
            attachments = []
            for attachment in post["attachments"]:
                cid = attachment["contentId"]
                if cid in media:
                    attachments.append(media[cid])
                elif cid in bundles:
                    bundle = bundles[cid]["bundleContent"]
                    bundle.sort(key=lambda c: c["pos"])
                    for c in bundle:
                        mid = c["accountMediaId"]
                        if mid in media:
                            attachments.append(media[mid])
                        else:
                            if extra is None:
                                post["_extra"] = extra = []
                            extra.append(mid)
                else:
                    self.extractor.log.warning(
                        "%s: Unhandled 'contentId' %s",
                        post["id"], cid)
            post["attachments"] = attachments

        return posts

    def _update_media(self, items, response):
        posts = {
            post["id"]: post
            for post in response["posts"]
        }

        response["posts"] = [
            posts[item["correlationId"]]
            for item in items
        ]

        return self._update_posts(response)

    def _update_items(self, items):
        ids = [item["id"] for item in items]
        accounts = {
            account["id"]: account
            for account in self.accounts_by_id(ids)
        }
        return [accounts[id] for id in ids]

    def _call(self, endpoint, params):
        url = f"{self.ROOT}/api{endpoint}"
        params["ngsw-bypass"] = "true"
        headers = self.headers.copy()
        headers["fansly-client-ts"] = str(int(time.time() * 1000))

        data = self.extractor.request_json(
            url, params=params, headers=headers)
        return data["response"]

    def _pagination(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            if not response.get("posts"):
                return
            posts = self._update_posts(response)
            yield from posts
            params["before"] = min(p["id"] for p in posts)

    def _pagination_list(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            if not response:
                return
            yield from self._update_items(response)
            params["after"] = response[-1]["sortId"]

    def _pagination_media(self, endpoint, params):
        while True:
            response = self._call(endpoint, params)

            data = response["data"]
            if not data:
                return
            yield from self._update_media(data, response["aggregationData"])
            params["before"] = data[-1]["id"]
