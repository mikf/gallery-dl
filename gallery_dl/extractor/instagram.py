# -*- coding: utf-8 -*-

# Copyright 2018-2020 Leonardo Taccari
# Copyright 2018-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.instagram.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import binascii
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
    cookies_domain = ".instagram.com"
    cookies_names = ("sessionid",)
    useragent = util.USERAGENT_CHROME
    request_interval = (6.0, 12.0)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def _init(self):
        self.www_claim = "0"
        self.csrf_token = util.generate_token()
        self._find_tags = re.compile(r"#\w+").findall
        self._logged_in = True
        self._cursor = None
        self._user = None

        self.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookies_domain)

        if self.config("api") == "graphql":
            self.api = InstagramGraphqlAPI(self)
        else:
            self.api = InstagramRestAPI(self)

    def items(self):
        self.login()

        data = self.metadata()
        videos = self.config("videos", True)
        if videos:
            videos_dash = (videos != "merged")
            videos_headers = {"User-Agent": "Mozilla/5.0"}
        previews = self.config("previews", False)
        max_posts = self.config("max-posts")

        order = self.config("order-files")
        reverse = order[0] in ("r", "d") if order else False

        posts = self.posts()
        if max_posts:
            posts = itertools.islice(posts, max_posts)

        for post in posts:

            if "__typename" in post:
                post = self._parse_post_graphql(post)
            else:
                post = self._parse_post_rest(post)
            if self._user:
                post["user"] = self._user
            post.update(data)
            files = post.pop("_files")

            post["count"] = len(files)
            yield Message.Directory, post

            if "date" in post:
                del post["date"]
            if reverse:
                files.reverse()

            for file in files:
                file.update(post)

                url = file.get("video_url")
                if url:
                    if videos:
                        file["_http_headers"] = videos_headers
                        text.nameext_from_url(url, file)
                        if videos_dash:
                            file["_fallback"] = (url,)
                            file["_ytdl_manifest"] = "dash"
                            url = "ytdl:dash"
                        yield Message.Url, url, file
                    if previews:
                        file["media_id"] += "p"
                    else:
                        continue

                url = file["display_url"]
                text.nameext_from_url(url, file)
                if file["extension"] == "webp" and "stp=dst-jpg" in url:
                    file["extension"] = "jpg"
                yield Message.Url, url, file

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def finalize(self):
        if self._cursor:
            self.log.info("Use '-o cursor=%s' to continue downloading "
                          "from the current position", self._cursor)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history:

            url = response.url
            if "/accounts/login/" in url:
                page = "login"
            elif "/challenge/" in url:
                page = "challenge"
            else:
                page = None

            if page:
                raise exception.StopExtraction("HTTP redirect to %s page (%s)",
                                               page, url.partition("?")[0])

        www_claim = response.headers.get("x-ig-set-www-claim")
        if www_claim is not None:
            self.www_claim = www_claim

        csrf_token = response.cookies.get("csrftoken")
        if csrf_token:
            self.csrf_token = csrf_token

        return response

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(_login_impl(self, username, password))

        self._logged_in = False

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

        else:  # regular image/video post
            data = {
                "post_id" : post["pk"],
                "post_shortcode": post["code"],
                "post_url": "{}/p/{}/".format(self.root, post["code"]),
                "likes": post.get("like_count", 0),
                "liked": post.get("has_liked", False),
                "pinned": self._extract_pinned(post),
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

            coauthors = post.get("coauthor_producers")
            if coauthors:
                data["coauthors"] = [
                    {"id"       : user["pk"],
                     "username" : user["username"],
                     "full_name": user["full_name"]}
                    for user in coauthors
                ]

            items = post.get("carousel_media")
            if items:
                data["sidecar_media_id"] = data["post_id"]
                data["sidecar_shortcode"] = data["post_shortcode"]
            else:
                items = (post,)

        owner = post["user"]
        data["owner_id"] = owner["pk"]
        data["username"] = owner.get("username")
        data["fullname"] = owner.get("full_name")
        data["post_date"] = data["date"] = text.parse_timestamp(
            post.get("taken_at") or post.get("created_at") or post.get("seen"))
        data["_files"] = files = []
        for num, item in enumerate(items, 1):

            try:
                image = item["image_versions2"]["candidates"][0]
            except Exception:
                self.log.warning("Missing media in post %s",
                                 data["post_shortcode"])
                continue

            video_versions = item.get("video_versions")
            if video_versions:
                video = max(
                    video_versions,
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
                "_ytdl_manifest_data": item.get("video_dash_manifest"),
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
            "likes"      : post["edge_media_preview_like"]["count"],
            "liked"      : post.get("viewer_has_liked", False),
            "pinned"     : pinned,
            "owner_id"   : owner["id"],
            "username"   : owner.get("username"),
            "fullname"   : owner.get("full_name"),
            "post_id"    : post["id"],
            "post_shortcode": post["shortcode"],
            "post_url"   : "{}/p/{}/".format(self.root, post["shortcode"]),
            "post_date"  : text.parse_timestamp(post["taken_at_timestamp"]),
            "description": text.parse_unicode_escapes("\n".join(
                edge["node"]["text"]
                for edge in post["edge_media_to_caption"]["edges"]
            )),
        }
        data["date"] = data["post_date"]

        tags = self._find_tags(data["description"])
        if tags:
            data["tags"] = sorted(set(tags))

        location = post.get("location")
        if location:
            data["location_id"] = location["id"]
            data["location_slug"] = location["slug"]
            data["location_url"] = "{}/explore/locations/{}/{}/".format(
                self.root, location["id"], location["slug"])

        coauthors = post.get("coauthor_producers")
        if coauthors:
            data["coauthors"] = [
                {"id"      : user["id"],
                 "username": user["username"]}
                for user in coauthors
            ]

        data["_files"] = files = []
        if "edge_sidecar_to_children" in post:
            for num, edge in enumerate(
                    post["edge_sidecar_to_children"]["edges"], 1):
                node = edge["node"]
                dimensions = node["dimensions"]
                media = {
                    "num": num,
                    "media_id"   : node["id"],
                    "date"       : data["date"],
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
                "date"       : data["date"],
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

    def _extract_pinned(self, post):
        return (post.get("timeline_pinned_user_ids") or
                post.get("clips_tab_pinned_user_ids") or ())

    def _init_cursor(self):
        cursor = self.config("cursor", True)
        if cursor is True:
            return None
        elif not cursor:
            self._update_cursor = util.identity
        return cursor

    def _update_cursor(self, cursor):
        self.log.debug("Cursor: %s", cursor)
        self._cursor = cursor
        return cursor

    def _assign_user(self, user):
        self._user = user

        for key, old in (
                ("count_media"     , "edge_owner_to_timeline_media"),
                ("count_video"     , "edge_felix_video_timeline"),
                ("count_saved"     , "edge_saved_media"),
                ("count_mutual"    , "edge_mutual_followed_by"),
                ("count_follow"    , "edge_follow"),
                ("count_followed"  , "edge_followed_by"),
                ("count_collection", "edge_media_collections")):
            try:
                user[key] = user.pop(old)["count"]
            except Exception:
                user[key] = 0


class InstagramUserExtractor(InstagramExtractor):
    """Extractor for an Instagram user profile"""
    subcategory = "user"
    pattern = USER_PATTERN + r"/?(?:$|[?#])"
    example = "https://www.instagram.com/USER/"

    def initialize(self):
        pass

    def finalize(self):
        pass

    def items(self):
        base = "{}/{}/".format(self.root, self.item)
        stories = "{}/stories/{}/".format(self.root, self.item)
        return self._dispatch_extractors((
            (InstagramInfoExtractor      , base + "info/"),
            (InstagramAvatarExtractor    , base + "avatar/"),
            (InstagramStoriesExtractor   , stories),
            (InstagramHighlightsExtractor, base + "highlights/"),
            (InstagramPostsExtractor     , base + "posts/"),
            (InstagramReelsExtractor     , base + "reels/"),
            (InstagramTaggedExtractor    , base + "tagged/"),
        ), ("posts",))


class InstagramPostsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's posts"""
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    example = "https://www.instagram.com/USER/posts/"

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.user_feed(uid)

    def _extract_pinned(self, post):
        try:
            return post["timeline_pinned_user_ids"]
        except KeyError:
            return ()


class InstagramReelsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's reels"""
    subcategory = "reels"
    pattern = USER_PATTERN + r"/reels"
    example = "https://www.instagram.com/USER/reels/"

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.user_clips(uid)

    def _extract_pinned(self, post):
        try:
            return post["clips_tab_pinned_user_ids"]
        except KeyError:
            return ()


class InstagramTaggedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's tagged posts"""
    subcategory = "tagged"
    pattern = USER_PATTERN + r"/tagged"
    example = "https://www.instagram.com/USER/tagged/"

    def metadata(self):
        if self.item.startswith("id:"):
            self.user_id = self.item[3:]
            return {"tagged_owner_id": self.user_id}

        self.user_id = self.api.user_id(self.item)
        user = self.api.user_by_name(self.item)

        return {
            "tagged_owner_id" : user["id"],
            "tagged_username" : user["username"],
            "tagged_full_name": user["full_name"],
        }

    def posts(self):
        return self.api.user_tagged(self.user_id)


class InstagramGuideExtractor(InstagramExtractor):
    """Extractor for an Instagram guide"""
    subcategory = "guide"
    pattern = USER_PATTERN + r"/guide/[^/?#]+/(\d+)"
    example = "https://www.instagram.com/USER/guide/NAME/12345"

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.guide_id = match.group(2)

    def metadata(self):
        return {"guide": self.api.guide(self.guide_id)}

    def posts(self):
        return self.api.guide_media(self.guide_id)


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's saved media"""
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved(?:/all-posts)?/?$"
    example = "https://www.instagram.com/USER/saved/"

    def posts(self):
        return self.api.user_saved()


class InstagramCollectionExtractor(InstagramExtractor):
    """Extractor for Instagram collection"""
    subcategory = "collection"
    pattern = USER_PATTERN + r"/saved/([^/?#]+)/([^/?#]+)"
    example = "https://www.instagram.com/USER/saved/COLLECTION/12345"

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
               r"/s(?:tories/(?:highlights/(\d+)|([^/?#]+)(?:/(\d+))?)"
               r"|/(aGlnaGxpZ2h0[^?#]+)(?:\?story_media_id=(\d+))?)")
    example = "https://www.instagram.com/stories/USER/"

    def __init__(self, match):
        h1, self.user, m1, h2, m2 = match.groups()

        if self.user:
            self.highlight_id = None
        else:
            self.subcategory = InstagramHighlightsExtractor.subcategory
            self.highlight_id = ("highlight:" + h1 if h1 else
                                 binascii.a2b_base64(h2).decode())

        self.media_id = m1 or m2
        InstagramExtractor.__init__(self, match)

    def posts(self):
        reel_id = self.highlight_id or self.api.user_id(self.user)
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
    example = "https://www.instagram.com/USER/highlights/"

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.highlights_media(uid)


class InstagramFollowingExtractor(InstagramExtractor):
    """Extractor for an Instagram user's followed users"""
    subcategory = "following"
    pattern = USER_PATTERN + r"/following"
    example = "https://www.instagram.com/USER/following/"

    def items(self):
        uid = self.api.user_id(self.item)
        for user in self.api.user_following(uid):
            user["_extractor"] = InstagramUserExtractor
            url = "{}/{}".format(self.root, user["username"])
            yield Message.Queue, url, user


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for Instagram tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = BASE_PATTERN + r"/explore/tags/([^/?#]+)"
    example = "https://www.instagram.com/explore/tags/TAG/"

    def metadata(self):
        return {"tag": text.unquote(self.item)}

    def posts(self):
        return self.api.tags_media(self.item)


class InstagramInfoExtractor(InstagramExtractor):
    """Extractor for an Instagram user's profile data"""
    subcategory = "info"
    pattern = USER_PATTERN + r"/info"
    example = "https://www.instagram.com/USER/info/"

    def items(self):
        screen_name = self.item
        if screen_name.startswith("id:"):
            user = self.api.user_by_id(screen_name[3:])
        else:
            user = self.api.user_by_name(screen_name)

        return iter(((Message.Directory, user),))


class InstagramAvatarExtractor(InstagramExtractor):
    """Extractor for an Instagram user's avatar"""
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.instagram.com/USER/avatar/"

    def posts(self):
        if self._logged_in:
            user_id = self.api.user_id(self.item, check_private=False)
            user = self.api.user_by_id(user_id)
            avatar = (user.get("hd_profile_pic_url_info") or
                      user["hd_profile_pic_versions"][-1])
        else:
            user = self.item
            if user.startswith("id:"):
                user = self.api.user_by_id(user[3:])
            else:
                user = self.api.user_by_name(user)
                user["pk"] = user["id"]
            url = user.get("profile_pic_url_hd") or user["profile_pic_url"]
            avatar = {"url": url, "width": 0, "height": 0}

        pk = user.get("profile_pic_id")
        if pk:
            pk = pk.partition("_")[0]
            code = shortcode_from_id(pk)
        else:
            pk = code = "avatar:" + str(user["pk"])

        return ({
            "pk"        : pk,
            "code"      : code,
            "user"      : user,
            "caption"   : None,
            "like_count": 0,
            "image_versions2": {"candidates": (avatar,)},
        },)


class InstagramPostExtractor(InstagramExtractor):
    """Extractor for an Instagram post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?:[^/?#]+/)?(?:p|tv|reel)/([^/?#]+)")
    example = "https://www.instagram.com/p/abcdefg/"

    def posts(self):
        return self.api.media(self.item)


class InstagramRestAPI():

    def __init__(self, extractor):
        self.extractor = extractor

    def guide(self, guide_id):
        endpoint = "/v1/guides/web_info/"
        params = {"guide_id": guide_id}
        return self._call(endpoint, params=params)

    def guide_media(self, guide_id):
        endpoint = "/v1/guides/guide/{}/".format(guide_id)
        return self._pagination_guides(endpoint)

    def highlights_media(self, user_id, chunk_size=5):
        reel_ids = [hl["id"] for hl in self.highlights_tray(user_id)]

        order = self.extractor.config("order-posts")
        if order:
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
        endpoint = "/v1/highlights/{}/highlights_tray/".format(user_id)
        return self._call(endpoint)["tray"]

    def media(self, shortcode):
        if len(shortcode) > 28:
            shortcode = shortcode[:-28]
        endpoint = "/v1/media/{}/info/".format(id_from_shortcode(shortcode))
        return self._pagination(endpoint)

    def reels_media(self, reel_ids):
        endpoint = "/v1/feed/reels_media/"
        params = {"reel_ids": reel_ids}
        try:
            return self._call(endpoint, params=params)["reels_media"]
        except KeyError:
            raise exception.AuthorizationError("Login required")

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
    def user_by_name(self, screen_name):
        endpoint = "/v1/users/web_profile_info/"
        params = {"username": screen_name}
        return self._call(
            endpoint, params=params, notfound="user")["data"]["user"]

    @memcache(keyarg=1)
    def user_by_id(self, user_id):
        endpoint = "/v1/users/{}/info/".format(user_id)
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
        endpoint = "/v1/feed/collection/{}/posts/".format(collection_id)
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_feed(self, user_id):
        endpoint = "/v1/feed/user/{}/".format(user_id)
        params = {"count": 30}
        return self._pagination(endpoint, params)

    def user_following(self, user_id):
        endpoint = "/v1/friendships/{}/following/".format(user_id)
        params = {"count": 12}
        return self._pagination_following(endpoint, params)

    def user_saved(self):
        endpoint = "/v1/feed/saved/posts/"
        params = {"count": 50}
        return self._pagination(endpoint, params, media=True)

    def user_tagged(self, user_id):
        endpoint = "/v1/usertags/{}/feed/".format(user_id)
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

            if "next_max_id" not in data:
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(data["next_max_id"])

    def _pagination_following(self, endpoint, params):
        extr = self.extractor
        params["max_id"] = text.parse_int(extr._init_cursor())

        while True:
            data = self._call(endpoint, params=params)

            yield from data["users"]

            if len(data["users"]) < params["count"]:
                return extr._update_cursor(None)
            params["max_id"] = extr._update_cursor(
                params["max_id"] + params["count"])


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

    @staticmethod
    def _unsupported(_=None):
        raise exception.StopExtraction("Unsupported with GraphQL API")

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
        return extr.request(url, params=params, headers=headers).json()["data"]

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
                s = "" if self.extractor.item.endswith("s") else "s"
                raise exception.StopExtraction(
                    "%s'%s posts are private", self.extractor.item, s)

            variables["after"] = extr._update_cursor(info["end_cursor"])


@cache(maxage=90*86400, keyarg=1)
def _login_impl(extr, username, password):
    extr.log.error("Login with username & password is no longer supported. "
                   "Use browser cookies instead.")
    return {}


def id_from_shortcode(shortcode):
    return util.bdecode(shortcode, _ALPHABET)


def shortcode_from_id(post_id):
    return util.bencode(int(post_id), _ALPHABET)


_ALPHABET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789-_")
