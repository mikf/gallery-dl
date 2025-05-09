# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/ using TikWM's API"""

from .common import Extractor, Message
from .. import text, util, exception
import logging

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktokv?\.com"


class TikwmExtractor(Extractor):
    """Base class for TikTok extractors"""
    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = (
        "{id}{num:?_//>02} {title[b:150]}{img_id|audio_id:? [/]/}.{extension}")
    archive_fmt = "{id}_{num}_{img_id}"
    root = "https://www.tiktok.com"
    api_root = "https://tikwm.com/api"
    request_interval = 3.0

    def __init__(self, match):
        if isinstance(match, str):
            self.url = match
            pattern = getattr(self, "pattern", self.pattern)
            self.match = util.re_compile(pattern).search(match)

            if self.match:
                self.groups = self.match.groups()
            else:
                self.groups = ()

            self.log = logging.getLogger(self.category)
            self._cfgpath = ("extractor", self.category, self.subcategory)
            self._parentdir = ""

            self.request_interval = self.config(
                "sleep-request", self.request_interval)

            # Enforce minimum request_interval
            if self.request_interval < 1.0:
                self.log.warning("sleep-request must be at least 1.0")
                # self.request_interval = 1.0
                # TODO: fix failing enforcement

            self.initialize()
        else:
            Extractor.__init__(self, match)

    def _init(self):
        self.video = self.config("videos", True)
        self.hd = self.config("tikwm-hd", True)
        self.audio = self.config("audio", True)
        self._cursor = None

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

    def finalize(self):
        if self._cursor:
            self.log.info("Use '-o cursor=%s' to continue downloading "
                          "from the current position", self._cursor)

    def _api_request(self, endpoint="", params=None):
        """Make an API request to tikwm.com"""
        url = self.api_root
        if endpoint:
            url += "/" + endpoint

        if endpoint == "video/detail":
            video_id = params.get("video_id")
            url = f"{self.api_root}/?url={video_id}"
            if self.hd:
                url += "&hd=1"
            params = None

        response = self.request(url, params=params)
        try:
            data = response.json()
        except ValueError:
            raise exception.StopExtraction("Failed to parse JSON response")

        if data.get("code") == 0:
            return data.get("data")

        msg = data.get("msg", "").lower()
        if "free api limit" in msg:
            raise exception.StopExtraction("Tikwm API rate limit reached")

        raise exception.StopExtraction(
            "Tikwm API error: %s (%d)", data.get("msg"), data.get("code"))

    def _parse_post_data(self, post_data):
        """Parse TikTok post data into a standardized dictionary"""
        post_id = post_data.get("id", "") or post_data.get("video_id", "")

        post = {
            # Author information
            "author": {
                "id": post_data.get("author", {}).get("id", ""),
                "uniqueId": post_data.get("author", {}).get("unique_id", ""),
                "nickname": post_data.get("author", {}).get("nickname", ""),
                "avatarLarger": post_data.get("author", {}).get("avatar", ""),
            },

            # Post information
            "id": post_id,
            "desc": post_data.get("title", ""),
            "title": post_data.get("title", ""),
            "createTime": post_data.get("create_time", 0),
            "date": text.parse_timestamp(post_data.get("create_time", 0)),
            "duration": post_data.get("duration", 0),
            "play": post_data.get("play", ""),
            "wmplay": post_data.get("wmplay", ""),
            "hdplay": post_data.get("hdplay", ""),
            "size": post_data.get("size", 0),
            "wm_size": post_data.get("wm_size", 0),
            "hd_size": post_data.get("hd_size", 0),
            "region": post_data.get("region", ""),
            "cover": post_data.get("cover", ""),
            "ai_dynamic_cover": post_data.get("ai_dynamic_cover", ""),
            "origin_cover": post_data.get("origin_cover", ""),
            "mentioned_users": post_data.get("mentioned_users", ""),

            # Music info
            "music_info": post_data.get("music_info", {}),
            "music": post_data.get("music", ""),

            # Statistics
            "play_count": post_data.get("play_count", 0),
            "digg_count": post_data.get("digg_count", 0),
            "comment_count": post_data.get("comment_count", 0),
            "share_count": post_data.get("share_count", 0),
            "download_count": post_data.get("download_count", 0),
            "collect_count": post_data.get("collect_count", 0),

            # Flags and additional info
            "is_ad": post_data.get("is_ad", False),
            "item_comment_settings": post_data.get("item_comment_settings", 0),
            "anchors": post_data.get("anchors", None),
            "anchors_extras": post_data.get("anchors_extras", ""),

            # Commerce info
            "commerce_info": post_data.get("commerce_info", {}),
            "commercial_video_info": post_data.get(
                "commercial_video_info", ""),
        }

        # Add images array if present
        if post_data.get("images"):
            post["images"] = post_data.get("images", [])

        if "is_top" in post_data:
            post["is_top"] = post_data.get("is_top", 0)

        return post

    def _extract_post(self, tiktok_url):
        """Extract a single TikTok post"""
        params = {"url": tiktok_url}
        if self.hd:
            params["hd"] = "1"

        post_data = self._api_request("", params)
        if not post_data:
            self.log.error("Failed to extract post data for %s", tiktok_url)
            return None

        post = self._parse_post_data(post_data)
        return post, post_data

    def _extract_media(self, post, post_data):
        """Extract media items from a post"""
        if not post or not post_data:
            return

        # Handle images if present
        if post_data.get("images"):
            if not post["desc"]:
                post["title"] = "TikTok photo #{}".format(post["id"])
            else:
                post["title"] = post["desc"]

            for i, img_url in enumerate(post_data["images"], 1):
                text.nameext_from_url(img_url, post)
                post.update({
                    "type": "image",
                    "title": post["title"],
                    "num": i,
                    "img_id": post["id"] + "_" + str(i),
                })
                yield Message.Url, img_url, post

            if self.audio and post_data.get("music"):
                audio_url = None
                if isinstance(post_data["music"], dict):
                    audio_url = post_data["music"].get(
                        "play") or post_data["music"].get("play_url")
                elif isinstance(post_data["music"], str):
                    audio_url = post_data["music"]

                if audio_url:
                    text.nameext_from_url(audio_url, post)
                    post.update({
                        "type": "audio",
                        "image": None,
                        "title": post["desc"] or "TikTok audio #{}".format(
                            post["id"]),
                        "num": 0,
                        "img_id": "",
                        "audio_id": (post_data.get(
                            "music_info", {}).get(
                                "id") or (
                                    post_data["music"].get("id") if isinstance(
                                        post_data.get("music"), dict) else "")
                        ),
                    })
                    if not post["extension"]:
                        post["extension"] = "mp3"
                    yield Message.Url, audio_url, post

        elif self.video and post_data.get("play"):
            if not post["desc"]:
                post["title"] = "TikTok video #{}".format(post["id"])
            else:
                post["title"] = post["desc"]

            video_url = post_data["play"]
            if self.hd and post_data.get("hdplay"):
                video_url = post_data["hdplay"]

            text.nameext_from_url(video_url, post)
            post.update({
                "type": "video",
                "image": None,
                "num": 0,
                "img_id": "",
            })
            if not post["extension"]:
                post["extension"] = "mp4"
            yield Message.Url, video_url, post

            if self.audio:
                audio_url = None
                if isinstance(post_data.get("music"), dict):
                    audio_url = post_data["music"].get("play") or (
                        post_data["music"].get("play_url")
                    )
                elif isinstance(post_data.get("music"), str):
                    audio_url = post_data["music"]
                elif post_data.get("music_info", {}).get("play"):
                    audio_url = post_data["music_info"]["play"]

                if audio_url:
                    audio_post = post.copy()
                    text.nameext_from_url(audio_url, audio_post)
                    audio_post.update({
                        "type": "audio",
                        "image": None,
                        "title": post["desc"] or "TikTok audio #{}".format(
                            post["id"]
                        ),
                        "num": 0,
                        "img_id": "",
                        "audio_id": (post_data.get(
                            "music_info", {}).get("id") or (
                                post_data["music"].get("id") if isinstance(
                                    post_data.get("music"), dict) else "")
                        ),
                    })
                    if not audio_post["extension"]:
                        audio_post["extension"] = "mp3"
                    yield Message.Url, audio_url, audio_post


class TikwmPostExtractor(TikwmExtractor):
    """Extract a single video or photo TikTok link, or by post ID"""
    subcategory = "post"
    pattern = BASE_PATTERN + \
        r"/(?:pid:(\d+)|(?:@([\w_.-]*)|share)/(?:phot|vide)o/(\d+))"
    example = "https://www.tiktok.com/@USER/photo/1234567890"

    def items(self):
        pid, user, post_id = self.groups
        if pid:
            url = pid
        else:
            url = "{}/@{}/video/{}".format(self.root, user or "", post_id)
            url = self._sanitize_url(url)

        post, post_data = self._extract_post(url)
        if not post:
            return

        yield Message.Directory, post
        yield from self._extract_media(post, post_data)

    def _sanitize_url(self, url):
        return text.ensure_http_scheme(url.replace("/photo/", "/video/", 1))


class TikwmVmpostExtractor(TikwmExtractor):
    """Extract a single video or photo TikTok VM link"""
    subcategory = "vmpost"
    pattern = (r"(?:https?://)?(?:"
               r"v[mt]\.tiktok\.com"
               r"|(?:www\.)?tiktok\.com/t"
               r")/(?!@)([^/?#]+)")
    example = "https://vm.tiktok.com/1a2B3c4E5"

    def items(self):
        url = text.ensure_http_scheme(self.url)

        url = self.request_location(url, notfound="post")
        if not url or len(url) <= 28:
            raise exception.NotFoundError("post")

        post, post_data = self._extract_post(url)
        if not post:
            return

        yield Message.Directory, post
        yield from self._extract_media(post, post_data)


class TikwmUserExtractor(TikwmExtractor):
    """Extract a TikTok user's profile"""
    subcategory = "user"
    batch_size = 10
    pattern = BASE_PATTERN + r"/(?:@([\w_.-]+)|id:(\d+))/?(?:$|\?|#)"
    example = "https://www.tiktok.com/@USER"

    def _init(self):
        TikwmExtractor._init(self)
        self.avatar = self.config("avatar", True)
        self.batch_size = self.config("tikwm-batch-size", self.batch_size)

        # Enforce maximum batch_size
        if self.batch_size > 33:
            self.log.warning("batch_size cannot exceed 33")
            self.batch_size = 33

    def items(self):
        user_name, user_id = self.groups

        if user_id:
            identifier = {"user_id": user_id}
        else:
            if user_name.isdigit():
                identifier = {"user_id": user_name}
            else:
                identifier = {"unique_id": user_name}

        if self.avatar:
            user_data = self._api_request("user/info", identifier)
            if not user_data:
                raise exception.NotFoundError("user")

            avatar_url, avatar = self._generate_avatar(user_name, user_data)
            yield Message.Directory, avatar
            yield Message.Url, avatar_url, avatar

        cursor = self._init_cursor() or "0"
        count = 0

        while True:
            if cursor != "0":
                self.log.debug("Fetching posts from cursor: %s", cursor)

            feed_data = self._api_request("user/posts", {
                **identifier,
                "count": str(self.batch_size),
                "cursor": cursor
            })

            if not feed_data or not feed_data.get("videos"):
                if cursor == "0":
                    break
                break

            for post_data in feed_data["videos"]:
                video_id = post_data.get("video_id", "")

                if self.hd and not post_data.get("hdplay"):
                    video_detail = self._api_request(
                        "video/detail", {"video_id": video_id})

                    if video_detail and video_detail.get("hdplay"):
                        post_data = video_detail

                post = self._parse_post_data(post_data)

                yield Message.Directory, post
                yield from self._extract_media(post, post_data)

                count += 1

            has_more = feed_data.get("hasMore")
            if not has_more:
                self._update_cursor(None)
                self.log.debug("No more posts available")
                break

            next_cursor = feed_data.get("cursor", "")
            if not next_cursor or next_cursor == "0":
                self._update_cursor(None)
                self.log.debug("Invalid cursor received")
                break

            cursor = self._update_cursor(next_cursor)

    def _generate_avatar(self, user_name, user_data):
        # Look for avatars inside the user object
        user_obj = user_data.get("user", {})

        avatar_fields = ["avatarLarger",
                         "avatarMedium", "avatarThumb", "avatar"]
        avatar_url = None

        for field in avatar_fields:
            if user_obj.get(field):
                avatar_url = user_obj.get(field)
                break

        if not avatar_url:
            avatar_url = user_data.get("avatar")

        if not avatar_url:
            raise exception.NotFoundError("avatar")

        data = {
            "id": user_obj.get("id", "") or user_data.get("id", ""),
        }

        user_id = user_obj.get("id", "") or user_data.get("id", "")
        if user_name is None:
            identifier = "id:" + user_id
        else:
            identifier = "@" + user_name

        avatar = text.nameext_from_url(avatar_url, data.copy())
        avatar.update({
            "type": "avatar",
            "title": identifier,
            "img_id": (user_name or user_id) + "_avatar",
            "num": 0,
        })

        return avatar_url, avatar
