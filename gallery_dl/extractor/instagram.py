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
        self.api = None
        self.www_claim = "0"
        self.csrf_token = util.generate_token()
        self._logged_in = True
        self._find_tags = re.compile(r"#\w+").findall
        self._cursor = None

    def items(self):
        self.login()

        api = self.config("api")
        if api is None or api == "auto":
            api = InstagramRestAPI if self._logged_in else InstagramGraphqlAPI
        elif api == "graphql":
            api = InstagramGraphqlAPI
        else:
            api = InstagramRestAPI
        self.api = api(self)

        data = self.metadata()
        videos = self.config("videos", True)
        previews = self.config("previews", False)
        video_headers = {"User-Agent": "Mozilla/5.0"}

        for post in self.posts():

            if "__typename" in post:
                post = self._parse_post_graphql(post)
            else:
                post = self._parse_post_rest(post)
            post.update(data)
            files = post.pop("_files")

            post["count"] = len(files)
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

    def login(self):
        self._username = None
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            if username:
                self._username = username
                self._update_cookies(_login_impl(self, username, password))
            else:
                self._logged_in = False
        self.session.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookiedomain)

    def _parse_post_rest(self, post):
        if "items" in post:  # story or highlight
            items = post["items"]
            reel_id = str(post["id"]).rpartition(":")[2]
            data = {
                "expires": text.parse_timestamp(post.get("expiring_at")),
                "post_id": reel_id,
                "post_shortcode": shortcode_from_id(reel_id),
            }

            if "title" in post:
                data["highlight_title"] = post["title"]
            if "created_at" in post:
                data["date"] = text.parse_timestamp(post.get("created_at"))

        else:  # regular image/video post
            data = {
                "post_id" : post["pk"],
                "post_shortcode": post["code"],
                "likes": post["like_count"],
                "pinned": post.get("timeline_pinned_user_ids", ()),
                "date": text.parse_timestamp(post.get("taken_at")),
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

    def _parse_post_graphql(self, post):
        typename = post["__typename"]

        if self._logged_in:
            if post.get("is_video") and "video_url" not in post:
                post = self.api.media(post["id"])[0]
            elif typename == "GraphSidecar" and \
                    "edge_sidecar_to_children" not in post:
                post = self.api.media(post["id"])[0]

        pinned = post.get("pinned_for_users", ())
        if pinned:
            for index, user in enumerate(pinned):
                pinned[index] = int(user["id"])

        owner = post["owner"]
        data = {
            "typename"   : typename,
            "date"       : text.parse_timestamp(post["taken_at_timestamp"]),
            "likes"      : post["edge_media_preview_like"]["count"],
            "pinned"     : pinned,
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

    def _init_cursor(self):
        return self.config("cursor") or None

    def _update_cursor(self, cursor):
        self.log.debug("Cursor: %s", cursor)
        self._cursor = cursor
        return cursor


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
            (InstagramTaggedExtractor    , base + "tagged/"),
            (InstagramChannelExtractor   , base + "channel/"),
        ), ("posts",))


class InstagramPostsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's posts"""
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    test = ("https://www.instagram.com/instagram/posts/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.user_feed(uid)


class InstagramReelsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's reels"""
    subcategory = "reels"
    pattern = USER_PATTERN + r"/reels"
    test = ("https://www.instagram.com/instagram/reels/", {
        "range": "40-60",
        "count": ">= 20",
    })

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.user_clips(uid)


class InstagramTaggedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's tagged posts"""
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

        self.user_id = self.api.user_id(self.item)
        user = self.api.user(self.item)

        return {
            "tagged_owner_id" : user["id"],
            "tagged_username" : user["username"],
            "tagged_full_name": user["full_name"],
        }

    def posts(self):
        return self.api.user_tagged(self.user_id)


class InstagramChannelExtractor(InstagramExtractor):
    """Extractor for an Instagram user's channel posts"""
    subcategory = "channel"
    pattern = USER_PATTERN + r"/channel"
    test = ("https://www.instagram.com/instagram/channel/", {
        "range": "1-16",
        "count": ">= 16",
    })

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.user_clips(uid)


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's saved media"""
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved(?:/all-posts)?/?$"
    test = (
        ("https://www.instagram.com/instagram/saved/"),
        ("https://www.instagram.com/instagram/saved/all-posts/"),
    )

    def posts(self):
        return self.api.user_saved()


class InstagramCollectionExtractor(InstagramExtractor):
    """Extractor for Instagram collection"""
    subcategory = "collection"
    pattern = USER_PATTERN + r"/saved/([^/?#]+)/([^/?#]+)"
    test = (
        "https://www.instagram.com/instagram/saved/collection_name/123456789/",
    )

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.user, self.collection_name, self.collection_id = match.groups()

    def metadata(self):
        return {
            "collection_id"  : self.collection_id,
            "collection_name": text.unescape(self.collection_name),
        }

    def posts(self):
        return self.api.user_collection(self.collection_id)


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
            reel_id = self.api.user_id(self.user)

        reels = self.api.reels_media(reel_id)

        if self.media_id and reels:
            reel = reels[0]
            for item in reel["items"]:
                if item["pk"] == self.media_id:
                    reel["items"] = (item,)
                    break
            else:
                raise exception.NotFoundError("story")

        return reels


class InstagramHighlightsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's story highlights"""
    subcategory = "highlights"
    pattern = USER_PATTERN + r"/highlights"
    test = ("https://www.instagram.com/instagram/highlights",)

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.highlights_media(uid)


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for Instagram tags"""
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
        return self.api.tags_media(self.item)


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
        return self.api.media(id_from_shortcode(self.item))


class InstagramRestAPI():

    def __init__(self, extractor):
        self.extractor = extractor

    def highlights_media(self, user_id):
        chunk_size = 5
        reel_ids = [hl["id"] for hl in self.highlights_tray(user_id)]

        for offset in range(0, len(reel_ids), chunk_size):
            yield from self.reels_media(
                reel_ids[offset : offset+chunk_size])

    def highlights_tray(self, user_id):
        endpoint = "/v1/highlights/{}/highlights_tray/".format(user_id)
        return self._call(endpoint)["tray"]

    def media(self, post_id):
        endpoint = "/v1/media/{}/info/".format(post_id)
        return self._pagination(endpoint)

    def reels_media(self, reel_ids):
        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_ids}
        return self._call(endpoint, params=params)["reels_media"]

    def tags_media(self, tag):
        for section in self.tags_sections(tag):
            for media in section["layout_content"]["medias"]:
                yield media["media"]

    def tags_sections(self, tag):
        endpoint = "/v1/tags/{}/sections/".format(tag)
        data = {
            "include_persistent": "0",
            "max_id" : None,
            "page"   : None,
            "surface": "grid",
            "tab"    : "recent",
        }
        return self._pagination_sections(endpoint, data)

    @memcache(keyarg=1)
    def user(self, screen_name):
        endpoint = "/v1/users/web_profile_info/"
        params = {"username": screen_name}
        return self._call(endpoint, params=params)["data"]["user"]

    def user_id(self, screen_name):
        if screen_name.startswith("id:"):
            return screen_name[3:]
        user = self.user(screen_name)
        if user is None:
            raise exception.AuthorizationError(
                "Login required to access this profile")
        if user["is_private"] and not user["followed_by_viewer"]:
            name = user["username"]
            s = "" if name.endswith("s") else "s"
            raise exception.StopExtraction("%s'%s posts are private", name, s)
        return user["id"]

    def user_clips(self, user_id):
        endpoint = "/v1/clips/user/"
        data = {"target_user_id": user_id, "page_size": "50"}
        return self._pagination_post(endpoint, data)

    def user_collection(self, collection_id):
        endpoint = "/v1/feed/collection/{}/posts/".format(collection_id)
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_feed(self, user_id):
        endpoint = "/v1/feed/user/{}/".format(user_id)
        params = {"count": 30}
        return self._pagination(endpoint, params)

    def user_saved(self):
        endpoint = "/v1/feed/saved/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_tagged(self, user_id):
        endpoint = "/v1/usertags/{}/feed/".format(user_id)
        params = {"count": 50}
        return self._pagination(endpoint, params)

    def _call(self, endpoint, **kwargs):
        extr = self.extractor

        url = "https://i.instagram.com/api" + endpoint
        kwargs["headers"] = {
            "X-CSRFToken"     : extr.csrf_token,
            "X-Instagram-AJAX": "1006242110",
            "X-IG-App-ID"     : "936619743392459",
            "X-ASBD-ID"       : "198387",
            "X-IG-WWW-Claim"  : extr.www_claim,
            "Origin"          : extr.root,
            "Referer"         : extr.root + "/",
        }
        kwargs["cookies"] = {
            "csrftoken": extr.csrf_token,
        }
        return extr.request(url, **kwargs).json()

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
                return
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
                return
            params["max_id"] = extr._update_cursor(info["max_id"])

    def _pagination_sections(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = extr._init_cursor()

        while True:
            info = self._call(endpoint, method="POST", data=params)

            yield from info["sections"]

            if not info.get("more_available"):
                return
            params["page"] = info["next_page"]
            params["max_id"] = extr._update_cursor(info["next_max_id"])


class InstagramGraphqlAPI():

    def __init__(self, extractor):
        self.extractor = extractor
        self.user_collection = self.user_saved = self.reels_media = \
            self.highlights_media = self._login_required
        self._json_dumps = json.JSONEncoder(separators=(",", ":")).encode

        api = InstagramRestAPI(extractor)
        self.user = api.user
        self.user_id = api.user_id

    @staticmethod
    def _login_required(_=None):
        raise exception.AuthorizationError("Login required")

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

    def media(self, post_id):
        query_hash = "9f8827793ef34641b2fb195d4d41151c"
        variables = {
            "shortcode": shortcode_from_id(post_id),
            "child_comment_count": 3,
            "fetch_comment_count": 40,
            "parent_comment_count": 24,
            "has_threaded_comments": True,
        }
        media = self._call(query_hash, variables).get("shortcode_media")
        return (media,) if media else ()

    def tags_media(self, tag):
        query_hash = "9b498c08113f1e09617a1703c22b2f32"
        variables = {"tag_name": text.unescape(tag), "first": 50}
        return self._pagination(query_hash, variables,
                                "hashtag", "edge_hashtag_to_media")

    def user_clips(self, user_id):
        query_hash = "bc78b344a68ed16dd5d7f264681c4c76"
        variables = {"id": user_id, "first": 50}
        return self._pagination(query_hash, variables)

    def user_feed(self, user_id):
        query_hash = "69cba40317214236af40e7efa697781d"
        variables = {"id": user_id, "first": 50}
        return self._pagination(query_hash, variables)

    def user_tagged(self, user_id):
        query_hash = "be13233562af2d229b008d2976b998b5"
        variables = {"id": user_id, "first": 50}
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
        cookies = {
            "csrftoken": extr.csrf_token,
        }
        return extr.request(
            url, params=params, headers=headers, cookies=cookies,
        ).json()["data"]

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
                return
            elif not data["edges"]:
                s = "" if self.item.endswith("s") else "s"
                raise exception.StopExtraction(
                    "%s'%s posts are private", self.item, s)

            variables["after"] = extr._update_cursor(info["end_cursor"])


@cache(maxage=90*24*3600, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.info("Logging in as %s", username)

    user_agent = ("Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/106.0.5249.79 Mobile "
                  "Safari/537.36 Instagram 255.1.0.17.102")

    headers = {
        "User-Agent"    : user_agent,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    url = extr.root + "/accounts/login/"
    response = extr.request(url, headers=headers)

    extract = text.extract_from(response.text)
    csrf_token = extract('"csrf_token":"', '"')
    device_id = extract('"device_id":"', '"')
    rollout_hash = extract('"rollout_hash":"', '"')

    cset = extr.session.cookies.set
    cset("csrftoken", csrf_token, domain=extr.cookiedomain)
    cset("ig_did", device_id, domain=extr.cookiedomain)

    headers = {
        "User-Agent"      : user_agent,
        "Accept"          : "*/*",
        "X-CSRFToken"     : csrf_token,
        "X-Instagram-AJAX": rollout_hash,
        "X-IG-App-ID"     : "936619743392459",
        "X-ASBD-ID"       : "198387",
        "X-IG-WWW-Claim"  : "0",
        "X-Requested-With": "XMLHttpRequest",
        "Origin"          : extr.root,
        "Referer"         : url,
        "Sec-Fetch-Dest"  : "empty",
        "Sec-Fetch-Mode"  : "cors",
        "Sec-Fetch-Site"  : "same-origin",
    }
    data = {
        "enc_password"        : "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(
            int(time.time()), password),
        "username"            : username,
        "queryParams"         : "{}",
        "optIntoOneTap"       : "false",
        "stopDeletionNonce"   : "",
        "trustedDeviceRecords": "{}",
    }
    url = extr.root + "/accounts/login/ajax/"
    response = extr.request(url, method="POST", headers=headers, data=data)

    if not response.json().get("authenticated"):
        raise exception.AuthenticationError()

    return {cookie.name: cookie.value
            for cookie in extr.session.cookies}


def id_from_shortcode(shortcode):
    return util.bdecode(shortcode, _ALPHABET)


def shortcode_from_id(post_id):
    return util.bencode(int(post_id), _ALPHABET)


_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789-_")
