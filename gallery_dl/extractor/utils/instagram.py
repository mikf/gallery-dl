# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from ... import text, util, exception
from ...cache import memcache


_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789-_")


def id_from_shortcode(shortcode):
    return util.bdecode(shortcode, _ALPHABET)


class InstagramRestAPI():

    def __init__(self, extractor):
        self.extractor = extractor

    def guide(self, guide_id):
        endpoint = "/v1/guides/web_info/"
        params = {"guide_id": guide_id}
        return self._call(endpoint, params=params)

    def guide_media(self, guide_id):
        endpoint = f"/v1/guides/guide/{guide_id}/"
        return self._pagination_guides(endpoint)

    def highlights_media(self, user_id, chunk_size=5):
        reel_ids = [hl["id"] for hl in self.highlights_tray(user_id)]

        if order := self.extractor.config("order-posts"):
            if order in ("desc", "reverse"):
                reel_ids.reverse()
            elif order in ("id", "id_asc"):
                reel_ids.sort(key=lambda r: int(r[10:]))
            elif order == "id_desc":
                reel_ids.sort(key=lambda r: int(r[10:]), reverse=True)
            elif order != "asc":
                self.extractor.log.warning("Unknown posts order '%s'", order)

        for offset in range(0, len(reel_ids), chunk_size):
            yield from self.reels_media(
                reel_ids[offset : offset+chunk_size])

    def highlights_tray(self, user_id):
        endpoint = f"/v1/highlights/{user_id}/highlights_tray/"
        return self._call(endpoint)["tray"]

    def media(self, shortcode):
        if len(shortcode) > 28:
            shortcode = shortcode[:-28]
        endpoint = f"/v1/media/{id_from_shortcode(shortcode)}/info/"
        return self._pagination(endpoint)

    def reels_media(self, reel_ids):
        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_ids}
        try:
            return self._call(endpoint, params=params)["reels_media"]
        except KeyError:
            raise exception.AuthRequired("authenticated cookies")

    def reels_tray(self):
        endpoint = "/v1/feed/reels_tray/"
        return self._call(endpoint)["tray"]

    def tags_media(self, tag):
        for section in self.tags_sections(tag):
            for media in section["layout_content"]["medias"]:
                yield media["media"]

    def tags_sections(self, tag):
        endpoint = f"/v1/tags/{tag}/sections/"
        data = {
            "include_persistent": "0",
            "max_id" : None,
            "page"   : None,
            "surface": "grid",
            "tab"    : "recent",
        }
        return self._pagination_sections(endpoint, data)

    @memcache(keyarg=1)
    def user_by_name(self, screen_name):
        endpoint = "/v1/users/web_profile_info/"
        params = {"username": screen_name}
        return self._call(
            endpoint, params=params, notfound="user")["data"]["user"]

    @memcache(keyarg=1)
    def user_by_id(self, user_id):
        endpoint = f"/v1/users/{user_id}/info/"
        return self._call(endpoint)["user"]

    def user_id(self, screen_name, check_private=True):
        if screen_name.startswith("id:"):
            if self.extractor.config("metadata"):
                self.extractor._user = self.user_by_id(screen_name[3:])
            return screen_name[3:]

        user = self.user_by_name(screen_name)
        if user is None:
            raise exception.AuthorizationError(
                "Login required to access this profile")
        if check_private and user["is_private"] and \
                not user["followed_by_viewer"]:
            name = user["username"]
            s = "" if name.endswith("s") else "s"
            self.extractor.log.warning("%s'%s posts are private", name, s)
        self.extractor._assign_user(user)
        return user["id"]

    def user_clips(self, user_id):
        endpoint = "/v1/clips/user/"
        data = {
            "target_user_id": user_id,
            "page_size": "50",
            "max_id": None,
            "include_feed_video": "true",
        }
        return self._pagination_post(endpoint, data)

    def user_collection(self, collection_id):
        endpoint = f"/v1/feed/collection/{collection_id}/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_feed(self, user_id):
        endpoint = f"/v1/feed/user/{user_id}/"
        params = {"count": 30}
        return self._pagination(endpoint, params)

    def user_followers(self, user_id):
        endpoint = f"/v1/friendships/{user_id}/followers/"
        params = {"count": 12}
        return self._pagination_following(endpoint, params)

    def user_following(self, user_id):
        endpoint = f"/v1/friendships/{user_id}/following/"
        params = {"count": 12}
        return self._pagination_following(endpoint, params)

    def user_saved(self):
        endpoint = "/v1/feed/saved/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_tagged(self, user_id):
        endpoint = f"/v1/usertags/{user_id}/feed/"
        params = {"count": 20}
        return self._pagination(endpoint, params)

    def _call(self, endpoint, **kwargs):
        extr = self.extractor

        url = "https://www.instagram.com/api" + endpoint
        kwargs["headers"] = {
            "Accept"          : "*/*",
            "X-CSRFToken"     : extr.csrf_token,
            "X-IG-App-ID"     : "936619743392459",
            "X-ASBD-ID"       : "129477",
            "X-IG-WWW-Claim"  : extr.www_claim,
            "X-Requested-With": "XMLHttpRequest",
            "Connection"      : "keep-alive",
            "Referer"         : extr.root + "/",
            "Sec-Fetch-Dest"  : "empty",
            "Sec-Fetch-Mode"  : "cors",
            "Sec-Fetch-Site"  : "same-origin",
        }
        return extr.request_json(url, **kwargs)

    def _pagination(self, endpoint, params=None, media=False):
        if params is None:
            params = {}
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            data = self._call(endpoint, params=params)

            if media:
                for item in data["items"]:
                    yield item["media"]
            else:
                yield from data["items"]

            if not data.get("more_available"):
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(data["next_max_id"])

    def _pagination_post(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            data = self._call(endpoint, method="POST", data=params)

            for item in data["items"]:
                yield item["media"]

            info = data["paging_info"]
            if not info.get("more_available"):
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(info["max_id"])

    def _pagination_sections(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            info = self._call(endpoint, method="POST", data=params)

            yield from info["sections"]

            if not info.get("more_available"):
                return extr._update_cursor(None)
            params["page"] = info["next_page"]
            params["max_id"] = extr._update_cursor(info["next_max_id"])

    def _pagination_guides(self, endpoint):
        extr = self.extractor
        params = {"max_id": extr._init_cursor()}

        while True:
            data = self._call(endpoint, params=params)

            for item in data["items"]:
                yield from item["media_items"]

            next_max_id = data.get("next_max_id")
            if not next_max_id:
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(next_max_id)

    def _pagination_following(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = text.parse_int(extr._init_cursor())

        while True:
            data = self._call(endpoint, params=params)

            yield from data["users"]

            next_max_id = data.get("next_max_id")
            if not next_max_id:
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(next_max_id)


class InstagramGraphqlAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.user_collection = self.user_saved = self.reels_media = \
            self.highlights_media = self.guide = self.guide_media = \
            self._unsupported
        self._json_dumps = util.json_dumps

        api = InstagramRestAPI(extractor)
        self.user_by_name = api.user_by_name
        self.user_by_id = api.user_by_id
        self.user_id = api.user_id

    def _unsupported(self, _=None):
        raise exception.AbortExtraction("Unsupported with GraphQL API")

    def highlights_tray(self, user_id):
        query_hash = "d4d88dc1500312af6f937f7b804c68c3"
        variables = {
            "user_id": user_id,
            "include_chaining": False,
            "include_reel": False,
            "include_suggested_users": False,
            "include_logged_out_extras": True,
            "include_highlight_reels": True,
            "include_live_status": False,
        }
        edges = (self._call(query_hash, variables)["user"]
                 ["edge_highlight_reels"]["edges"])
        return [edge["node"] for edge in edges]

    def media(self, shortcode):
        query_hash = "9f8827793ef34641b2fb195d4d41151c"
        variables = {
            "shortcode": shortcode,
            "child_comment_count": 3,
            "fetch_comment_count": 40,
            "parent_comment_count": 24,
            "has_threaded_comments": True,
        }
        media = self._call(query_hash, variables).get("shortcode_media")
        return (media,) if media else ()

    def tags_media(self, tag):
        query_hash = "9b498c08113f1e09617a1703c22b2f32"
        variables = {"tag_name": text.unescape(tag), "first": 24}
        return self._pagination(query_hash, variables,
                                "hashtag", "edge_hashtag_to_media")

    def user_clips(self, user_id):
        query_hash = "bc78b344a68ed16dd5d7f264681c4c76"
        variables = {"id": user_id, "first": 24}
        return self._pagination(query_hash, variables)

    def user_feed(self, user_id):
        query_hash = "69cba40317214236af40e7efa697781d"
        variables = {"id": user_id, "first": 24}
        return self._pagination(query_hash, variables)

    def user_tagged(self, user_id):
        query_hash = "be13233562af2d229b008d2976b998b5"
        variables = {"id": user_id, "first": 24}
        return self._pagination(query_hash, variables)

    def _call(self, query_hash, variables):
        extr = self.extractor

        url = "https://www.instagram.com/graphql/query/"
        params = {
            "query_hash": query_hash,
            "variables" : self._json_dumps(variables),
        }
        headers = {
            "Accept"          : "*/*",
            "X-CSRFToken"     : extr.csrf_token,
            "X-Instagram-AJAX": "1006267176",
            "X-IG-App-ID"     : "936619743392459",
            "X-ASBD-ID"       : "198387",
            "X-IG-WWW-Claim"  : extr.www_claim,
            "X-Requested-With": "XMLHttpRequest",
            "Referer"         : extr.root + "/",
        }
        return extr.request_json(url, params=params, headers=headers)["data"]

    def _pagination(self, query_hash, variables,
                    key_data="user", key_edge=None):
        extr = self.extractor
        variables["after"] = extr._init_cursor()

        while True:
            data = self._call(query_hash, variables)[key_data]
            data = data[key_edge] if key_edge else next(iter(data.values()))

            for edge in data["edges"]:
                yield edge["node"]

            info = data["page_info"]
            if not info["has_next_page"]:
                return extr._update_cursor(None)
            elif not data["edges"]:
                user = self.extractor.item
                s = "" if user.endswith("s") else "s"
                raise exception.AbortExtraction(
                    f"{user}'{s} posts are private")

            variables["after"] = extr._update_cursor(info["end_cursor"])
