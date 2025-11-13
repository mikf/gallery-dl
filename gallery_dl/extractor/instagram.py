# -*- coding: utf-8 -*-

# Copyright 2018-2020 Leonardo Taccari
# Copyright 2018-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.instagram.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache, memcache
import itertools
import binascii

BASE_PATTERN = r"(?:https?://)?(?:www\.)?instagram\.com"
USER_PATTERN = rf"{BASE_PATTERN}/(?!(?:p|tv|reel|explore|stories)/)([^/?#]+)"


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
        self.item = match[1]

    def _init(self):
        self.www_claim = "0"
        self.csrf_token = util.generate_token()
        self._find_tags = text.re(r"#\w+").findall
        self._logged_in = True
        self._cursor = None
        self._user = None

        self.cookies.set(
            "csrftoken", self.csrf_token, domain=self.cookies_domain)

        if self.config("api") == "graphql":
            self.api = InstagramGraphqlAPI(self)
        else:
            self.api = InstagramRestAPI(self)

        self._warn_video = True if self.config("warn-videos", True) else False
        self._warn_image = (
            9 if not (wi := self.config("warn-images", True)) else
            1 if wi in ("all", "both") else
            0)

    def items(self):
        self.login()

        data = self.metadata()
        if videos := self.config("videos", True):
            self.videos_dash = videos_dash = (videos != "merged")
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

                if url := file.get("video_url"):
                    if videos:
                        file["_http_headers"] = videos_headers
                        text.nameext_from_url(url, file)
                        if videos_dash and "_ytdl_manifest_data" in file:
                            file["_fallback"] = (url,)
                            file["_ytdl_manifest"] = "dash"
                            url = f"ytdl:{post['post_url']}{file['num']}.mp4"
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

            if page is not None:
                raise exception.AbortExtraction(
                    f"HTTP redirect to {page} page ({url.partition('?')[0]})")

        www_claim = response.headers.get("x-ig-set-www-claim")
        if www_claim is not None:
            self.www_claim = www_claim

        if csrf_token := response.cookies.get("csrftoken"):
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
            if expires := post.get("expiring_at"):
                post_url = f"{self.root}/stories/{post['user']['username']}/"
            else:
                post_url = f"{self.root}/stories/highlights/{reel_id}/"
            data = {
                "user"   : post.get("user"),
                "expires": self.parse_timestamp(expires),
                "post_id": reel_id,
                "post_shortcode": shortcode_from_id(reel_id),
                "post_url": post_url,
                "type": "story" if expires else "highlight",
            }
            if "title" in post:
                data["highlight_title"] = post["title"]
            if expires and not post.get("seen"):
                post["seen"] = expires - 86400

        else:  # regular image/video post
            data = {
                "post_id" : post["pk"],
                "post_shortcode": post["code"],
                "likes": post.get("like_count", 0),
                "liked": post.get("has_liked", False),
                "pinned": self._extract_pinned(post),
            }

            caption = post["caption"]
            data["description"] = caption["text"] if caption else ""

            if tags := self._find_tags(data["description"]):
                data["tags"] = sorted(set(tags))

            if location := post.get("location"):
                slug = location["short_name"].replace(" ", "-").lower()
                data["location_id"] = location["pk"]
                data["location_slug"] = slug
                data["location_url"] = \
                    f"{self.root}/explore/locations/{location['pk']}/{slug}/"

            if coauthors := post.get("coauthor_producers"):
                data["coauthors"] = [
                    {"id"       : user["pk"],
                     "username" : user["username"],
                     "full_name": user["full_name"]}
                    for user in coauthors
                ]

            if items := post.get("carousel_media"):
                data["sidecar_media_id"] = data["post_id"]
                data["sidecar_shortcode"] = data["post_shortcode"]
            else:
                items = (post,)

        owner = post["user"]
        data["owner_id"] = owner["pk"]
        data["username"] = owner.get("username")
        data["fullname"] = owner.get("full_name")
        data["post_date"] = data["date"] = self.parse_timestamp(
            post.get("taken_at") or post.get("created_at") or post.get("seen"))
        data["_files"] = files = []
        for num, item in enumerate(items, 1):

            try:
                image = item["image_versions2"]["candidates"][0]
            except Exception:
                self.log.warning("Missing media in post %s",
                                 data["post_shortcode"])
                continue

            width_orig = item.get("original_width", 0)
            height_orig = item.get("original_height", 0)

            if video_versions := item.get("video_versions"):
                video = max(
                    video_versions,
                    key=lambda x: (x["width"], x["height"], x["type"]),
                )

                media = video
                if (manifest := item.get("video_dash_manifest")) and \
                        self.videos_dash:
                    width = width_orig
                    height = height_orig
                else:
                    width = video["width"]
                    height = video["height"]

                if self._warn_video:
                    self._warn_video = False
                    pattern = text.re(
                        r"Chrome/\d{3,}\.\d+\.\d+\.\d+(?!\d* Mobile)")
                    if not pattern.search(self.session.headers["User-Agent"]):
                        self.log.warning("Potentially lowered video quality "
                                         "due to non-Chrome User-Agent")
            else:
                video = manifest = None
                media = image
                width = image["width"]
                height = image["height"]

                if self._warn_image < ((width < width_orig) +
                                       (height < height_orig)):
                    self.log.warning(
                        "%s: Available image resolutions lower than the "
                        "original (%sx%s < %sx%s). "
                        "Consider refreshing your cookies.",
                        data["post_shortcode"],
                        width, height, width_orig, height_orig)

            media = {
                "num"        : num,
                "date"       : self.parse_timestamp(item.get("taken_at") or
                                                    media.get("taken_at") or
                                                    post.get("taken_at")),
                "media_id"   : item["pk"],
                "shortcode"  : (item.get("code") or
                                shortcode_from_id(item["pk"])),
                "display_url": image["url"],
                "video_url"  : video["url"] if video else None,
                "width"          : width,
                "width_original" : width_orig,
                "height"         : height,
                "height_original": height_orig,
            }

            if manifest is not None:
                media["_ytdl_manifest_data"] = manifest
            if "owner" in item:
                media["owner"] = item["owner"]
            if "reshared_story_media_author" in item:
                media["author"] = item["reshared_story_media_author"]
            if "expiring_at" in item:
                media["expires"] = self.parse_timestamp(post["expiring_at"])
            if "subscription_media_visibility" in item:
                media["subscription"] = item["subscription_media_visibility"]

            self._extract_tagged_users(item, media)
            files.append(media)

        if "subscription_media_visibility" in post:
            data["subscription"] = post["subscription_media_visibility"]
        if "type" not in data:
            if len(files) == 1 and files[0]["video_url"]:
                data["type"] = "reel"
                data["post_url"] = f"{self.root}/reel/{post['code']}/"
            else:
                data["type"] = "post"
                data["post_url"] = f"{self.root}/p/{post['code']}/"

        return data

    def _parse_post_graphql(self, post):
        typename = post["__typename"]

        if self._logged_in:
            if post.get("is_video") and "video_url" not in post:
                post = self.api.media(post["id"])[0]
            elif typename == "GraphSidecar" and \
                    "edge_sidecar_to_children" not in post:
                post = self.api.media(post["id"])[0]

        if pinned := post.get("pinned_for_users", ()):
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
            "post_url"   : f"{self.root}/p/{post['shortcode']}/",
            "post_date"  : self.parse_timestamp(post["taken_at_timestamp"]),
            "description": text.parse_unicode_escapes("\n".join(
                edge["node"]["text"]
                for edge in post["edge_media_to_caption"]["edges"]
            )),
        }
        data["date"] = data["post_date"]

        if tags := self._find_tags(data["description"]):
            data["tags"] = sorted(set(tags))

        if location := post.get("location"):
            data["location_id"] = location["id"]
            data["location_slug"] = location["slug"]
            data["location_url"] = (f"{self.root}/explore/locations/"
                                    f"{location['id']}/{location['slug']}/")

        if coauthors := post.get("coauthor_producers"):
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

    def _extract_tagged_users(self, src, dest):
        dest["tagged_users"] = tagged_users = []

        if edges := src.get("edge_media_to_tagged_user"):
            for edge in edges["edges"]:
                user = edge["node"]["user"]
                tagged_users.append({"id"       : user["id"],
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        if usertags := src.get("usertags"):
            for tag in usertags["in"]:
                user = tag["user"]
                tagged_users.append({"id"       : user["pk"],
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        if mentions := src.get("reel_mentions"):
            for mention in mentions:
                user = mention["user"]
                tagged_users.append({"id"       : user.get("pk"),
                                     "username" : user["username"],
                                     "full_name": user["full_name"]})

        if stickers := src.get("story_bloks_stickers"):
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
        if cursor:
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


class InstagramPostExtractor(InstagramExtractor):
    """Extractor for an Instagram post"""
    subcategory = "post"
    pattern = (r"(?:https?://)?(?:www\.)?instagram\.com"
               r"/(?:share()(?:/(?:p|tv|reels?()))?"
               r"|(?:[^/?#]+/)?(?:p|tv|reels?()))"
               r"/([^/?#]+)")
    example = "https://www.instagram.com/p/abcdefg/"

    def __init__(self, match):
        if match[2] is not None or match[3] is not None:
            self.subcategory = "reel"
        InstagramExtractor.__init__(self, match)

    def posts(self):
        share, _, _, shortcode = self.groups
        if share is not None:
            url = text.ensure_http_scheme(self.url)
            headers = {
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            }
            location = self.request_location(url, headers=headers)
            shortcode = location.split("/")[-2]
        return self.api.media(shortcode)


class InstagramUserExtractor(Dispatch, InstagramExtractor):
    """Extractor for an Instagram user profile"""
    pattern = rf"{USER_PATTERN}/?(?:$|[?#])"
    example = "https://www.instagram.com/USER/"

    def items(self):
        base = f"{self.root}/{self.item}/"
        stories = f"{self.root}/stories/{self.item}/"
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
    pattern = rf"{USER_PATTERN}/posts"
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
    pattern = rf"{USER_PATTERN}/reels"
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
    pattern = rf"{USER_PATTERN}/tagged"
    example = "https://www.instagram.com/USER/tagged/"

    def metadata(self):
        if self.item.startswith("id:"):
            self.user_id = self.item[3:]
            if not self.config("metadata"):
                return {"tagged_owner_id": self.user_id}
            user = self.api.user_by_id(self.user_id)
        else:
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
    pattern = rf"{USER_PATTERN}/guide/[^/?#]+/(\d+)"
    example = "https://www.instagram.com/USER/guide/NAME/12345"

    def __init__(self, match):
        InstagramExtractor.__init__(self, match)
        self.guide_id = match[2]

    def metadata(self):
        return {"guide": self.api.guide(self.guide_id)}

    def posts(self):
        return self.api.guide_media(self.guide_id)


class InstagramSavedExtractor(InstagramExtractor):
    """Extractor for an Instagram user's saved media"""
    subcategory = "saved"
    pattern = rf"{USER_PATTERN}/saved(?:/all-posts)?/?$"
    example = "https://www.instagram.com/USER/saved/"

    def posts(self):
        return self.api.user_saved()


class InstagramCollectionExtractor(InstagramExtractor):
    """Extractor for Instagram collection"""
    subcategory = "collection"
    pattern = rf"{USER_PATTERN}/saved/([^/?#]+)/([^/?#]+)"
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


class InstagramStoriesTrayExtractor(InstagramExtractor):
    """Extractor for your Instagram account's stories tray"""
    subcategory = "stories-tray"
    pattern = rf"{BASE_PATTERN}/stories/me/?$()"
    example = "https://www.instagram.com/stories/me/"

    def items(self):
        base = f"{self.root}/stories/id:"
        for story in self.api.reels_tray():
            story["date"] = self.parse_timestamp(story["latest_reel_media"])
            story["_extractor"] = InstagramStoriesExtractor
            yield Message.Queue, f"{base}{story['id']}/", story


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

        if not reels:
            return ()

        if self.media_id:
            reel = reels[0]
            for item in reel["items"]:
                if item["pk"] == self.media_id:
                    reel["items"] = (item,)
                    break
            else:
                raise exception.NotFoundError("story")

        elif self.config("split"):
            reel = reels[0]
            reels = []
            for item in reel["items"]:
                item.pop("user", None)
                copy = reel.copy()
                copy.update(item)
                copy["items"] = (item,)
                reels.append(copy)

        return reels


class InstagramHighlightsExtractor(InstagramExtractor):
    """Extractor for an Instagram user's story highlights"""
    subcategory = "highlights"
    pattern = rf"{USER_PATTERN}/highlights"
    example = "https://www.instagram.com/USER/highlights/"

    def posts(self):
        uid = self.api.user_id(self.item)
        return self.api.highlights_media(uid)


class InstagramFollowersExtractor(InstagramExtractor):
    """Extractor for an Instagram user's followers"""
    subcategory = "followers"
    pattern = rf"{USER_PATTERN}/followers"
    example = "https://www.instagram.com/USER/followers/"

    def items(self):
        uid = self.api.user_id(self.item)
        for user in self.api.user_followers(uid):
            user["_extractor"] = InstagramUserExtractor
            url = f"{self.root}/{user['username']}"
            yield Message.Queue, url, user


class InstagramFollowingExtractor(InstagramExtractor):
    """Extractor for an Instagram user's followed users"""
    subcategory = "following"
    pattern = rf"{USER_PATTERN}/following"
    example = "https://www.instagram.com/USER/following/"

    def items(self):
        uid = self.api.user_id(self.item)
        for user in self.api.user_following(uid):
            user["_extractor"] = InstagramUserExtractor
            url = f"{self.root}/{user['username']}"
            yield Message.Queue, url, user


class InstagramTagExtractor(InstagramExtractor):
    """Extractor for Instagram tags"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{subcategory}", "{tag}")
    pattern = rf"{BASE_PATTERN}/explore/tags/([^/?#]+)"
    example = "https://www.instagram.com/explore/tags/TAG/"

    def metadata(self):
        return {"tag": text.unquote(self.item)}

    def posts(self):
        return self.api.tags_media(self.item)


class InstagramInfoExtractor(InstagramExtractor):
    """Extractor for an Instagram user's profile data"""
    subcategory = "info"
    pattern = rf"{USER_PATTERN}/info"
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
    pattern = rf"{USER_PATTERN}/avatar"
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

        if pk := user.get("profile_pic_id"):
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
