# -*- coding: utf-8 -*-

# Copyright 2018-2020 Leonardo Taccari
# Copyright 2018-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.instagram.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
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
    request_interval = (6.0, 12.0)

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
        previews = self.config("previews", False)
        video_headers = {"User-Agent": "Mozilla/5.0"}

        for post in self.posts():

            if "__typename" in post:
                post = self._parse_post_graphql(post)
            else:
                post = self._parse_post_api(post)
            post.update(data)
            files = post.pop("_files")

            yield Message.Directory, post
            for file in files:
                file.update(post)

                url = file.get("video_url")
                if url:
                    if videos:
                        file["_http_headers"] = video_headers
                        text.nameext_from_url(url, file)
                        yield Message.Url, url, file
                    if not previews:
                        continue

                url = file["display_url"]
                yield Message.Url, url, text.nameext_from_url(url, file)

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history:

            url = response.url
            if "/accounts/login/" in url:
                if self._username:
                    self.log.debug("Invalidating cached login session for "
                                   "'%s'", self._username)
                    _login_impl.invalidate(self._username)
                page = "login"
            elif "/challenge/" in url:
                page = "challenge"
            else:
                page = None

            if page:
                if self._cursor:
                    self.log.info("Use '-o cursor=%s' to continue downloading "
                                  "from the current position", self._cursor)
                raise exception.StopExtraction("HTTP redirect to %s page (%s)",
                                               page, url.partition("?")[0])

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

    @memcache(keyarg=1)
    def _user_by_screen_name(self, screen_name):
        url = "https://www.instagram.com/{}/?__a=1&__d=dis".format(
            screen_name)
        headers = {
            "Referer": "https://www.instagram.com/{}/".format(screen_name),
            "X-CSRFToken"     : self.csrf_token,
            "X-IG-App-ID"     : "936619743392459",
            "X-IG-WWW-Claim"  : self.www_claim,
            "X-Requested-With": "XMLHttpRequest",
        }
        cookies = {
            "csrftoken": self.csrf_token,
        }
        return self.request(
            url, headers=headers, cookies=cookies).json()["graphql"]["user"]

    def _uid_by_screen_name(self, screen_name):
        if screen_name.startswith("id:"):
            return screen_name[3:]
        return self._user_by_screen_name(screen_name)["id"]

    def _media_by_id(self, post_id):
        endpoint = "/v1/media/{}/info/".format(post_id)
        return self._pagination_api(endpoint)

    def login(self):
        self._username = None
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self._username = username
                self._update_cookies(_login_impl(self, username, password))
        self.session.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookiedomain)

    def _parse_post_graphql(self, post):
        typename = post["__typename"]

        if post.get("is_video") and "video_url" not in post:
            media = next(self._media_by_id(post["id"]))
            return self._parse_post_api(media)

        if typename == "GraphSidecar" and \
                "edge_sidecar_to_children" not in post:
            media = next(self._media_by_id(post["id"]))
            return self._parse_post_api(media)

        owner = post["owner"]
        data = {
            "typename"   : typename,
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
                                    shortcode_from_id(node["id"])),
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

    def _parse_post_api(self, post):
        if "items" in post:
            items = post["items"]
            reel_id = str(post["id"]).rpartition(":")[2]
            data = {
                "expires": text.parse_timestamp(post.get("expiring_at")),
                "post_id": reel_id,
                "post_shortcode": shortcode_from_id(reel_id),
            }
        else:
            data = {
                "post_id" : post["pk"],
                "post_shortcode": post["code"],
                "likes": post["like_count"],
            }

            caption = post["caption"]
            data["description"] = caption["text"] if caption else ""

            tags = self._find_tags(data["description"])
            if tags:
                data["tags"] = sorted(set(tags))

            location = post.get("location")
            if location:
                slug = location["short_name"].replace(" ", "-").lower()
                data["location_id"] = location["pk"]
                data["location_slug"] = slug
                data["location_url"] = "{}/explore/locations/{}/{}/".format(
                    self.root, location["pk"], slug)

            if "carousel_media" in post:
                items = post["carousel_media"]
                data["sidecar_media_id"] = data["post_id"]
                data["sidecar_shortcode"] = data["post_shortcode"]
            else:
                items = (post,)

        owner = post["user"]
        data["owner_id"] = owner["pk"]
        data["username"] = owner.get("username")
        data["fullname"] = owner.get("full_name")
        data["post_url"] = "{}/p/{}/".format(self.root, data["post_shortcode"])

        data["_files"] = files = []
        for num, item in enumerate(items, 1):

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

            media = {
                "num"        : num,
                "date"       : text.parse_timestamp(item.get("taken_at") or
                                                    media.get("taken_at") or
                                                    post.get("taken_at")),
                "media_id"   : item["pk"],
                "shortcode"  : (item.get("code") or
                                shortcode_from_id(item["pk"])),
                "display_url": image["url"],
                "video_url"  : video["url"] if video else None,
                "width"      : media["width"],
                "height"     : media["height"],
            }

            if "expiring_at" in item:
                media["expires"] = text.parse_timestamp(post["expiring_at"])

            self._extract_tagged_users(item, media)
            files.append(media)

        return data

    @staticmethod
    def _extract_tagged_users(src, dest):
        dest["tagged_users"] = tagged_users = []

        edges = src.get("edge_media_to_tagged_user")
        if edges:
            for edge in edges["edges"]:
                user = edge["node"]["user"]
                tagged_users.append({"id"       : user["id"],
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        usertags = src.get("usertags")
        if usertags:
            for tag in usertags["in"]:
                user = tag["user"]
                tagged_users.append({"id"       : user["pk"],
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        mentions = src.get("reel_mentions")
        if mentions:
            for mention in mentions:
                user = mention["user"]
                tagged_users.append({"id"       : user.get("pk"),
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        stickers = src.get("story_bloks_stickers")
        if stickers:
            for sticker in stickers:
                sticker = sticker["bloks_sticker"]
                if sticker["bloks_sticker_type"] == "mention":
                    user = sticker["sticker_data"]["ig_mention"]
                    tagged_users.append({"id"       : user["account_id"],
                                         "username" : user["username"],
                                         "full_name": user["full_name"]})

    def _pagination_graphql(self, query_hash, variables):
        cursor = self.config("cursor")
        if cursor:
            variables["after"] = cursor

        while True:
            data = next(iter(self._request_graphql(
                query_hash, variables)["user"].values()))

            for edge in data["edges"]:
                yield edge["node"]

            info = data["page_info"]
            if not info["has_next_page"]:
                return
            elif not data["edges"]:
                s = "" if self.item.endswith("s") else "s"
                raise exception.StopExtraction(
                    "%s'%s posts are private", self.item, s)

            variables["after"] = self._cursor = info["end_cursor"]
            self.log.debug("Cursor: %s", self._cursor)

    def _pagination_api(self, endpoint, params=None):
        while True:
            data = self._request_api(endpoint, params=params)
            yield from data["items"]

            if not data["more_available"]:
                return
            params["max_id"] = data["next_max_id"]

    def _pagination_api_post(self, endpoint, params, post=False):
        while True:
            data = self._request_api(endpoint, method="POST", data=params)
            for item in data["items"]:
                yield item["media"]

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
        ("https://www.instagram.com/id:25025320/"),
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
            (InstagramTaggedExtractor    , base + "tagged/"),
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
        query_hash = "69cba40317214236af40e7efa697781d"
        variables = {"id": self._uid_by_screen_name(self.item), "first": 50}
        return self._pagination_graphql(query_hash, variables)


class InstagramTaggedExtractor(InstagramExtractor):
    """Extractor for ProfilePage tagged posts"""
    subcategory = "tagged"
    pattern = USER_PATTERN + r"/tagged"
    test = ("https://www.instagram.com/instagram/tagged/", {
        "range": "1-16",
        "count": ">= 16",
        "keyword": {
            "tagged_owner_id" : "25025320",
            "tagged_username" : "instagram",
            "tagged_full_name": "Instagram",
        },
    })

    def metadata(self):
        if self.item.startswith("id:"):
            self.user_id = self.item[3:]
            return {"tagged_owner_id": self.user_id}

        user = self._user_by_screen_name(self.item)
        self.user_id = user["id"]

        return {
            "tagged_owner_id" : user["id"],
            "tagged_username" : user["username"],
            "tagged_full_name": user["full_name"],
        }

    def posts(self):
        endpoint = "/v1/usertags/{}/feed/".format(self.user_id)
        params = {"count": 50}
        return self._pagination_api(endpoint, params)


class InstagramChannelExtractor(InstagramExtractor):
    """Extractor for ProfilePage channel"""
    subcategory = "channel"
    pattern = USER_PATTERN + r"/channel"
    test = ("https://www.instagram.com/instagram/channel/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def posts(self):
        query_hash = "bc78b344a68ed16dd5d7f264681c4c76"
        variables = {"id": self._uid_by_screen_name(self.item), "first": 50}
        return self._pagination_graphql(query_hash, variables)


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for ProfilePage saved media"""
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved"
    test = ("https://www.instagram.com/instagram/saved/",)

    def posts(self):
        query_hash = "2ce1d673055b99250e93b6f88f878fde"
        variables = {"id": self._uid_by_screen_name(self.item), "first": 50}
        return self._pagination_graphql(query_hash, variables)


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
        return {"tag": text.unquote(self.item)}

    def posts(self):
        endpoint = "/v1/tags/{}/sections/".format(self.item)
        data = {
            "include_persistent": "0",
            "max_id" : None,
            "page"   : None,
            "surface": "grid",
            "tab"    : "recent",
        }

        while True:
            info = self._request_api(endpoint, method="POST", data=data)

            for section in info["sections"]:
                for media in section["layout_content"]["medias"]:
                    yield media["media"]

            if not info.get("more_available"):
                return

            data["max_id"] = info["next_max_id"]
            data["page"] = info["next_page"]


class InstagramPostExtractor(InstagramExtractor):
    """Extractor for an Instagram post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?:[^/?#]+/)?(?:p|tv|reel)/([^/?#]+)")
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

        # URL with username (#2085)
        ("https://www.instagram.com/dm/p/CW042g7B9CY/"),

        ("https://www.instagram.com/reel/CDg_6Y1pxWu/"),
    )

    def posts(self):
        return self._media_by_id(id_from_shortcode(self.item))


class InstagramStoriesExtractor(InstagramExtractor):
    """Extractor for Instagram stories"""
    subcategory = "stories"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/stories/(?:highlights/(\d+)|([^/?#]+)(?:/(\d+))?)")
    test = (
        ("https://www.instagram.com/stories/instagram/"),
        ("https://www.instagram.com/stories/highlights/18042509488170095/"),
        ("https://instagram.com/stories/geekmig/2724343156064789461"),
    )

    def __init__(self, match):
        self.highlight_id, self.user, self.media_id = match.groups()
        if self.highlight_id:
            self.subcategory = InstagramHighlightsExtractor.subcategory
        InstagramExtractor.__init__(self, match)

    def posts(self):
        if self.highlight_id:
            reel_id = "highlight:" + self.highlight_id
        else:
            reel_id = self._uid_by_screen_name(self.user)

        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_id}
        reels = self._request_api(endpoint, params=params)["reels"]

        if self.media_id:
            reel = reels[reel_id]
            for item in reel["items"]:
                if item["pk"] == self.media_id:
                    reel["items"] = (item,)
                    break
            else:
                raise exception.NotFoundError("story")

        return reels.values()


class InstagramHighlightsExtractor(InstagramExtractor):
    """Extractor for all Instagram story highlights of a user"""
    subcategory = "highlights"
    pattern = USER_PATTERN + r"/highlights"
    test = ("https://www.instagram.com/instagram/highlights",)

    def posts(self):
        endpoint = "/v1/highlights/{}/highlights_tray/".format(
            self._uid_by_screen_name(self.item))
        tray = self._request_api(endpoint)["tray"]
        reel_ids = [highlight["id"] for highlight in tray]

        # Anything above 30 responds with statuscode 400.
        # 30 can work, however, sometimes the API will respond with 560 or 500.
        chunk_size = 5
        endpoint = "/v1/feed/reels_media/"

        for offset in range(0, len(reel_ids), chunk_size):
            chunk_ids = reel_ids[offset : offset+chunk_size]
            params = {"reel_ids": chunk_ids}
            reels = self._request_api(endpoint, params=params)["reels"]
            for reel_id in chunk_ids:
                yield reels[reel_id]


class InstagramReelsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's reels"""
    subcategory = "reels"
    pattern = USER_PATTERN + r"/reels"
    test = ("https://www.instagram.com/instagram/reels/", {
        "range": "40-60",
        "count": ">= 20",
    })

    def posts(self):
        endpoint = "/v1/clips/user/"
        data = {
            "target_user_id": self._uid_by_screen_name(self.item),
            "page_size"     : "50",
        }

        return self._pagination_api_post(endpoint, data)


@cache(maxage=360*24*3600, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    url = extr.root + "/accounts/login/"
    page = extr.request(url).text

    headers = {
        "X-Web-Device-Id" : text.extract(page, '"device_id":"', '"')[0],
        "X-IG-App-ID"     : "936619743392459",
        "X-ASBD-ID"       : "437806",
        "X-IG-WWW-Claim"  : "0",
        "X-Requested-With": "XMLHttpRequest",
        "Referer"         : url,
    }
    url = extr.root + "/data/shared_data/"
    data = extr.request(url, headers=headers).json()

    headers["X-CSRFToken"] = data["config"]["csrf_token"]
    headers["X-Instagram-AJAX"] = data["rollout_hash"]
    headers["Origin"] = extr.root
    data = {
        "username"     : username,
        "enc_password" : "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(
            int(time.time()), password),
        "queryParams"         : "{}",
        "optIntoOneTap"       : "false",
        "stopDeletionNonce"   : "",
        "trustedDeviceRecords": "{}",
    }
    url = extr.root + "/accounts/login/ajax/"
    response = extr.request(url, method="POST", headers=headers, data=data)

    if not response.json().get("authenticated"):
        raise exception.AuthenticationError()

    cget = extr.session.cookies.get
    return {
        name: cget(name)
        for name in ("sessionid", "mid", "ig_did")
    }


def id_from_shortcode(shortcode):
    return util.bdecode(shortcode, _ALPHABET)


def shortcode_from_id(post_id):
    return util.bencode(int(post_id), _ALPHABET)


_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789-_")
