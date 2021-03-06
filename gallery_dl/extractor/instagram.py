# -*- coding: utf-8 -*-

# Copyright 2018-2020 Leonardo Taccari
# Copyright 2018-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.instagram.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import json
import time
import re

BASE_PATTERN = r"(?:https?://)?(?:www\.)?instagram\.com"
USER_PATTERN = BASE_PATTERN + r"/(?!(?:p|tv|reel|explore|stories)/)([^/?#]+)"


class InstagramExtractor(Extractor):
    """Base class for instagram extractors"""
    category = "instagram"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = "{sidecar_media_id:?/_/}{media_id}.{extension}"
    archive_fmt = "{media_id}"
    root = "https://www.instagram.com"
    cookiedomain = ".instagram.com"
    cookienames = ("sessionid",)
    request_interval = 5.0

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)
        self.www_claim = "0"
        self.csrf_token = util.generate_token()
        self._find_tags = re.compile(r"#\w+").findall
        self._cursor = None

    def items(self):
        self.login()
        data = self.metadata()
        videos = self.config("videos", True)

        for post in self.posts():

            if "__typename" in post:
                post = self._parse_post_graphql(post)
            else:
                post = self._parse_post_reel(post)
            post.update(data)
            files = post.pop("_files")

            yield Message.Directory, post
            for file in files:
                url = file.get("video_url")
                if not url:
                    url = file["display_url"]
                elif not videos:
                    continue
                file.update(post)
                yield Message.Url, url, text.nameext_from_url(url, file)

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history and "/accounts/login/" in response.request.url:
            if self._cursor:
                self.log.info("Use '-o cursor=%s' to continue downloading "
                              "from the current position", self._cursor)
            raise exception.StopExtraction(
                "HTTP redirect to login page (%s)", response.request.url)

        www_claim = response.headers.get("x-ig-set-www-claim")
        if www_claim is not None:
            self.www_claim = www_claim

        return response

    def _request_api(self, endpoint, **kwargs):
        url = "https://i.instagram.com/api" + endpoint
        kwargs["headers"] = {
            "X-CSRFToken"   : self.csrf_token,
            "X-IG-App-ID"   : "936619743392459",
            "X-IG-WWW-Claim": self.www_claim,
        }
        kwargs["cookies"] = {
            "csrftoken": self.csrf_token,
        }
        return self.request(url, **kwargs).json()

    def _request_graphql(self, query_hash, variables):
        url = self.root + "/graphql/query/"
        params = {
            "query_hash": query_hash,
            "variables" : json.dumps(variables),
        }
        headers = {
            "X-CSRFToken"     : self.csrf_token,
            "X-IG-App-ID"     : "936619743392459",
            "X-IG-WWW-Claim"  : self.www_claim,
            "X-Requested-With": "XMLHttpRequest",
        }
        cookies = {
            "csrftoken": self.csrf_token,
        }
        return self.request(
            url, params=params, headers=headers, cookies=cookies,
        ).json()["data"]

    def login(self):
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self.session.cookies.set(
                    "ig_cb", "2", domain="www.instagram.com")
                self._update_cookies(self._login_impl(username, password))

        self.session.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookiedomain)

    @cache(maxage=360*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        page = self.request(self.root + "/accounts/login/").text
        headers = {
            "Referer"         : self.root + "/accounts/login/",
            "X-IG-App-ID"     : "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
        }

        response = self.request(self.root + "/web/__mid/", headers=headers)
        headers["X-CSRFToken"] = response.cookies["csrftoken"]
        headers["X-Instagram-AJAX"] = text.extract(
            page, '"rollout_hash":"', '"')[0]

        url = self.root + "/accounts/login/ajax/"
        data = {
            "username"     : username,
            "enc_password" : "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(
                int(time.time()), password),
            "queryParams"  : "{}",
            "optIntoOneTap": "false",
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.json().get("authenticated"):
            raise exception.AuthenticationError()
        return {
            key: self.session.cookies.get(key)
            for key in ("sessionid", "mid", "csrftoken")
        }

    def _parse_post_graphql(self, post):
        if post.get("is_video") and "video_url" not in post:
            url = "{}/tv/{}/".format(self.root, post["shortcode"])
            post = self._extract_post_page(url)

        owner = post["owner"]
        data = {
            "typename"   : post["__typename"],
            "date"       : text.parse_timestamp(post["taken_at_timestamp"]),
            "likes"      : post["edge_media_preview_like"]["count"],
            "owner_id"   : owner["id"],
            "username"   : owner.get("username"),
            "fullname"   : owner.get("full_name"),
            "post_id"    : post["id"],
            "post_shortcode": post["shortcode"],
            "post_url"   : "{}/p/{}/".format(self.root, post["shortcode"]),
            "description": text.parse_unicode_escapes("\n".join(
                edge["node"]["text"]
                for edge in post["edge_media_to_caption"]["edges"]
            )),
        }

        tags = self._find_tags(data["description"])
        if tags:
            data["tags"] = sorted(set(tags))

        location = post.get("location")
        if location:
            data["location_id"] = location["id"]
            data["location_slug"] = location["slug"]
            data["location_url"] = "{}/explore/locations/{}/{}/".format(
                self.root, location["id"], location["slug"])

        data["_files"] = files = []
        if "edge_sidecar_to_children" in post:
            for num, edge in enumerate(
                    post["edge_sidecar_to_children"]["edges"], 1):
                node = edge["node"]
                dimensions = node["dimensions"]
                media = {
                    "num": num,
                    "media_id"   : node["id"],
                    "shortcode"  : (node.get("shortcode") or
                                    self._shortcode_from_id(node["id"])),
                    "display_url": node["display_url"],
                    "video_url"  : node.get("video_url"),
                    "width"      : dimensions["width"],
                    "height"     : dimensions["height"],
                    "sidecar_media_id" : post["id"],
                    "sidecar_shortcode": post["shortcode"],
                }
                self._extract_tagged_users(node, media)
                files.append(media)
        else:
            dimensions = post["dimensions"]
            media = {
                "media_id"   : post["id"],
                "shortcode"  : post["shortcode"],
                "display_url": post["display_url"],
                "video_url"  : post.get("video_url"),
                "width"      : dimensions["width"],
                "height"     : dimensions["height"],
            }
            self._extract_tagged_users(post, media)
            files.append(media)

        return data

    def _parse_post_reel(self, post):

        if "media" in post:
            media = post["media"]
            owner = media["user"]
            post["items"] = (media,)
            data = {
                "post_id" : media["pk"],
                "post_shortcode": self._shortcode_from_id(media["pk"]),
            }
        else:
            reel_id = str(post["id"]).rpartition(":")[2]
            owner = post["user"]
            data = {
                "expires" : text.parse_timestamp(post.get("expiring_at")),
                "post_id" : reel_id,
                "post_shortcode": self._shortcode_from_id(reel_id),
            }

        data["owner_id"] = owner["pk"]
        data["username"] = owner.get("username")
        data["fullname"] = owner.get("full_name")
        data["_files"] = files = []

        for num, item in enumerate(post["items"], 1):

            image = item["image_versions2"]["candidates"][0]

            if "video_versions" in item:
                video = max(
                    item["video_versions"],
                    key=lambda x: (x["width"], x["height"], x["type"]),
                )
                media = video
            else:
                video = None
                media = image

            files.append({
                "num"        : num,
                "date"       : text.parse_timestamp(item["taken_at"]),
                "media_id"   : item["pk"],
                "shortcode"  : item["code"],
                "display_url": image["url"],
                "video_url"  : video["url"] if video else None,
                "width"      : media["width"],
                "height"     : media["height"],
            })

        return data

    @staticmethod
    def _shortcode_from_id(post_id):
        return util.bencode(
            int(post_id),
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789-_")

    def _extract_tagged_users(self, src, dest):
        if "edge_media_to_tagged_user" not in src:
            return
        edges = src["edge_media_to_tagged_user"]["edges"]
        if edges:
            dest["tagged_users"] = tagged_users = []
            for edge in edges:
                user = edge["node"]["user"]
                tagged_users.append({
                    "id"       : user["id"],
                    "username" : user["username"],
                    "full_name": user["full_name"],
                })

    def _extract_shared_data(self, url):
        page = self.request(url).text
        shared_data, pos = text.extract(
            page, "window._sharedData =", ";</script>")
        additional_data, pos = text.extract(
            page, "window.__additionalDataLoaded(", ");</script>", pos)

        data = json.loads(shared_data)
        if additional_data:
            next(iter(data["entry_data"].values()))[0] = \
                json.loads(additional_data.partition(",")[2])
        return data

    def _extract_profile_page(self, url):
        data = self._extract_shared_data(url)["entry_data"]
        if "HttpErrorPage" in data:
            raise exception.NotFoundError("user")
        return data["ProfilePage"][0]["graphql"]["user"]

    def _extract_post_page(self, url):
        data = self._extract_shared_data(url)["entry_data"]
        if "HttpErrorPage" in data:
            raise exception.NotFoundError("post")
        return data["PostPage"][0]["graphql"]["shortcode_media"]

    def _get_edge_data(self, user, key):
        cursor = self.config("cursor")
        if cursor:
            return {
                "edges"    : (),
                "page_info": {
                    "end_cursor"   : cursor,
                    "has_next_page": True,
                    "_virtual"     : True,
                },
            }
        return user[key]

    def _pagination_graphql(self, query_hash, variables, data):
        while True:
            for edge in data["edges"]:
                yield edge["node"]

            info = data["page_info"]
            if not info["has_next_page"]:
                return
            elif not data["edges"] and "_virtual" not in info:
                s = "" if self.item.endswith("s") else "s"
                raise exception.StopExtraction(
                    "%s'%s posts are private", self.item, s)

            variables["after"] = self._cursor = info["end_cursor"]
            self.log.debug("Cursor: %s", self._cursor)
            data = next(iter(self._request_graphql(
                query_hash, variables)["user"].values()))

    def _pagination_api(self, endpoint, params):
        while True:
            data = self._request_api(endpoint, method="POST", data=params)
            yield from data["items"]

            info = data["paging_info"]
            if not info["more_available"]:
                return
            params["max_id"] = info["max_id"]


class InstagramUserExtractor(InstagramExtractor):
    """Extractor for an Instagram user profile"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:$|[?#])"
    test = (
        ("https://www.instagram.com/instagram/"),
        ("https://www.instagram.com/instagram/?hl=en"),
    )

    def items(self):
        base = "{}/{}/".format(self.root, self.item)
        stories = "{}/stories/{}/".format(self.root, self.item)
        return self._dispatch_extractors((
            (InstagramStoriesExtractor   , stories),
            (InstagramHighlightsExtractor, base + "highlights/"),
            (InstagramPostsExtractor     , base + "posts/"),
            (InstagramReelsExtractor     , base + "reels/"),
            (InstagramChannelExtractor   , base + "channel/"),
        ), ("posts",))


class InstagramPostsExtractor(InstagramExtractor):
    """Extractor for ProfilePage posts"""
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    test = ("https://www.instagram.com/instagram/posts/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def posts(self):
        url = "{}/{}/".format(self.root, self.item)
        user = self._extract_profile_page(url)

        query_hash = "003056d32c2554def87228bc3fd9668a"
        variables = {"id": user["id"], "first": 50}
        edge = self._get_edge_data(user, "edge_owner_to_timeline_media")
        return self._pagination_graphql(query_hash, variables, edge)


class InstagramChannelExtractor(InstagramExtractor):
    """Extractor for ProfilePage channel"""
    subcategory = "channel"
    pattern = USER_PATTERN + r"/channel"
    test = ("https://www.instagram.com/instagram/channel/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def posts(self):
        url = "{}/{}/channel/".format(self.root, self.item)
        user = self._extract_profile_page(url)

        query_hash = "bc78b344a68ed16dd5d7f264681c4c76"
        variables = {"id": user["id"], "first": 50}
        edge = self._get_edge_data(user, "edge_felix_video_timeline")
        return self._pagination_graphql(query_hash, variables, edge)


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for ProfilePage saved media"""
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved"
    test = ("https://www.instagram.com/instagram/saved/",)

    def posts(self):
        url = "{}/{}/saved/".format(self.root, self.item)
        user = self._extract_profile_page(url)

        query_hash = "2ce1d673055b99250e93b6f88f878fde"
        variables = {"id": user["id"], "first": 50}
        edge = self._get_edge_data(user, "edge_saved_media")
        return self._pagination_graphql(query_hash, variables, edge)


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for TagPage"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = BASE_PATTERN + r"/explore/tags/([^/?#]+)"
    test = ("https://www.instagram.com/explore/tags/instagram/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def metadata(self):
        return {"tag": self.item}

    def posts(self):
        url = "{}/explore/tags/{}/".format(self.root, self.item)
        data = self._extract_shared_data(url)
        hashtag = data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]

        query_hash = "9b498c08113f1e09617a1703c22b2f32"
        variables = {"tag_name": hashtag["name"], "first": 50}
        edge = self._get_edge_data(hashtag, "edge_hashtag_to_media")
        return self._pagination_graphql(query_hash, variables, edge)

    def _pagination_graphql(self, query_hash, variables, data):
        while True:
            for edge in data["edges"]:
                yield edge["node"]

            info = data["page_info"]
            if not info["has_next_page"]:
                return

            variables["after"] = self._cursor = info["end_cursor"]
            self.log.debug("Cursor: %s", self._cursor)
            data = self._request_graphql(
                query_hash, variables)["hashtag"]["edge_hashtag_to_media"]


class InstagramPostExtractor(InstagramExtractor):
    """Extractor for an Instagram post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?:p|tv|reel)/([^/?#]+)")
    test = (
        # GraphImage
        ("https://www.instagram.com/p/BqvsDleB3lV/", {
            "pattern": r"https://[^/]+\.(cdninstagram\.com|fbcdn\.net)"
                       r"/v(p/[0-9a-f]+/[0-9A-F]+)?/t51.2885-15/e35"
                       r"/44877605_725955034447492_3123079845831750529_n.jpg",
            "keyword": {
                "date": "dt:2018-11-29 01:04:04",
                "description": str,
                "height": int,
                "likes": int,
                "location_id": "214424288",
                "location_slug": "hong-kong",
                "location_url": "re:/explore/locations/214424288/hong-kong/",
                "media_id": "1922949326347663701",
                "shortcode": "BqvsDleB3lV",
                "post_id": "1922949326347663701",
                "post_shortcode": "BqvsDleB3lV",
                "post_url": "https://www.instagram.com/p/BqvsDleB3lV/",
                "tags": ["#WHPsquares"],
                "typename": "GraphImage",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphSidecar
        ("https://www.instagram.com/p/BoHk1haB5tM/", {
            "count": 5,
            "keyword": {
                "sidecar_media_id": "1875629777499953996",
                "sidecar_shortcode": "BoHk1haB5tM",
                "post_id": "1875629777499953996",
                "post_shortcode": "BoHk1haB5tM",
                "post_url": "https://www.instagram.com/p/BoHk1haB5tM/",
                "num": int,
                "likes": int,
                "username": "instagram",
            }
        }),

        # GraphVideo
        ("https://www.instagram.com/p/Bqxp0VSBgJg/", {
            "pattern": r"/46840863_726311431074534_7805566102611403091_n\.mp4",
            "keyword": {
                "date": "dt:2018-11-29 19:23:58",
                "description": str,
                "height": int,
                "likes": int,
                "media_id": "1923502432034620000",
                "post_url": "https://www.instagram.com/p/Bqxp0VSBgJg/",
                "shortcode": "Bqxp0VSBgJg",
                "tags": ["#ASMR"],
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphVideo (IGTV)
        ("https://www.instagram.com/tv/BkQjCfsBIzi/", {
            "pattern": r"/10000000_597132547321814_702169244961988209_n\.mp4",
            "keyword": {
                "date": "dt:2018-06-20 19:51:32",
                "description": str,
                "height": int,
                "likes": int,
                "media_id": "1806097553666903266",
                "post_url": "https://www.instagram.com/p/BkQjCfsBIzi/",
                "shortcode": "BkQjCfsBIzi",
                "typename": "GraphVideo",
                "username": "instagram",
                "width": int,
            }
        }),

        # GraphSidecar with 2 embedded GraphVideo objects
        ("https://www.instagram.com/p/BtOvDOfhvRr/", {
            "count": 2,
            "keyword": {
                "post_url": "https://www.instagram.com/p/BtOvDOfhvRr/",
                "sidecar_media_id": "1967717017113261163",
                "sidecar_shortcode": "BtOvDOfhvRr",
                "video_url": str,
            }
        }),

        # GraphImage with tagged user
        ("https://www.instagram.com/p/B_2lf3qAd3y/", {
            "keyword": {
                "tagged_users": [{
                    "id"       : "1246468638",
                    "username" : "kaaymbl",
                    "full_name": "Call Me Kay",
                }]
            }
        }),

        ("https://www.instagram.com/reel/CDg_6Y1pxWu/"),
    )

    def posts(self):
        query_hash = "2c4c2e343a8f64c625ba02b2aa12c7f8"
        variables = {
            "shortcode"            : self.item,
            "child_comment_count"  : 3,
            "fetch_comment_count"  : 40,
            "parent_comment_count" : 24,
            "has_threaded_comments": True
        }
        data = self._request_graphql(query_hash, variables)
        media = data.get("shortcode_media")
        if not media:
            raise exception.NotFoundError("post")
        return (media,)


class InstagramStoriesExtractor(InstagramExtractor):
    """Extractor for Instagram stories"""
    subcategory = "stories"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/stories/(?:highlights/(\d+)|([^/?#]+))")
    test = (
        ("https://www.instagram.com/stories/instagram/"),
        ("https://www.instagram.com/stories/highlights/18042509488170095/"),
    )
    request_interval = 1.0

    def __init__(self, match):
        self.highlight_id, self.user = match.groups()
        if self.highlight_id:
            self.subcategory = InstagramHighlightsExtractor.subcategory
        InstagramExtractor.__init__(self, match)

    def posts(self):
        if self.highlight_id:
            reel_id = "highlight:" + self.highlight_id
        else:
            url = "{}/stories/{}/".format(self.root, self.user)
            try:
                data = self._extract_shared_data(url)["entry_data"]
                user = data["StoriesPage"][0]["user"]
            except KeyError:
                return ()
            reel_id = user["id"]

        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_id}
        return self._request_api(endpoint, params=params)["reels"].values()


class InstagramHighlightsExtractor(InstagramExtractor):
    """Extractor for all Instagram story highlights of a user"""
    subcategory = "highlights"
    pattern = USER_PATTERN + r"/highlights"
    test = ("https://www.instagram.com/instagram/highlights",)

    def posts(self):
        url = "{}/{}/".format(self.root, self.item)
        user = self._extract_profile_page(url)

        query_hash = "d4d88dc1500312af6f937f7b804c68c3"
        variables = {
            "user_id": user["id"],
            "include_chaining": False,
            "include_reel": True,
            "include_suggested_users": False,
            "include_logged_out_extras": False,
            "include_highlight_reels": True,
            "include_live_status": True,
        }
        data = self._request_graphql(query_hash, variables)
        edges = data["user"]["edge_highlight_reels"]["edges"]
        if not edges:
            return ()

        reel_ids = ["highlight:" + edge["node"]["id"] for edge in edges]
        endpoint = "/v1/feed/reels_media/?reel_ids=" + \
                   "&reel_ids=".join(text.quote(rid) for rid in reel_ids)
        reels = self._request_api(endpoint)["reels"]
        return [reels[rid] for rid in reel_ids]


class InstagramReelsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's reels"""
    subcategory = "reels"
    pattern = USER_PATTERN + r"/reels"
    test = ("https://www.instagram.com/instagram/reels/", {
        "range": "40-60",
        "count": ">= 20",
    })

    def posts(self):
        url = "{}/{}/".format(self.root, self.item)
        user = self._extract_profile_page(url)

        endpoint = "/v1/clips/user/"
        data = {
            "target_user_id": user["id"],
            "page_size"     : "50",
        }

        return self._pagination_api(endpoint, data)
