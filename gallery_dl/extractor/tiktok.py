# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from itertools import count
from math import floor
from random import choices, randint
from re import fullmatch
from string import hexdigits
from time import time
from urllib.parse import quote
from .common import Extractor, Message
from .. import text, util, ytdl, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktokv?\.com"
SEC_UID_PATTERN = r"MS4wLjABAAAA[\w-]{64}"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""
    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = (
        "{id}{num:?_//>02} {title[b:150]}{img_id|audio_id:? [/]/}.{extension}")
    archive_fmt = "{id}_{num}_{img_id}"
    root = "https://www.tiktok.com"
    cookies_domain = ".tiktok.com"

    def _init(self):
        self.audio = self.config("audio", True)
        self.video = self.config("videos", True)
        self.cover = self.config("covers", False)

    def items(self):
        for tiktok_url in self.urls():
            tiktok_url = self._sanitize_url(tiktok_url)
            data = self._extract_rehydration_data(tiktok_url)
            if "webapp.video-detail" not in data:
                # Only /video/ links result in the video-detail dict we need.
                # Try again using that form of link.
                tiktok_url = self._sanitize_url(
                    data["seo.abtest"]["canonical"])
                data = self._extract_rehydration_data(tiktok_url)
            video_detail = data["webapp.video-detail"]

            if not self._check_status_code(video_detail, tiktok_url, "post"):
                continue

            post = video_detail["itemInfo"]["itemStruct"]
            post["user"] = (a := post.get("author")) and a["uniqueId"] or ""
            post["date"] = self.parse_timestamp(post["createTime"])
            original_title = title = post["desc"]

            yield Message.Directory, "", post
            ytdl_media = False

            if "imagePost" in post:
                if not original_title:
                    title = f"TikTok photo #{post['id']}"
                img_list = post["imagePost"]["images"]
                for i, img in enumerate(img_list, 1):
                    url = img["imageURL"]["urlList"][0]
                    text.nameext_from_url(url, post)
                    post.update({
                        "type"  : "image",
                        "image" : img,
                        "title" : title,
                        "num"   : i,
                        "img_id": post["filename"].partition("~")[0],
                        "width" : img["imageWidth"],
                        "height": img["imageHeight"],
                    })
                    yield Message.Url, url, post

                if self.audio and "music" in post:
                    if self.audio == "ytdl":
                        ytdl_media = "audio"
                    elif url := self._extract_audio(post):
                        yield Message.Url, url, post

            elif "video" in post:
                if self.video == "ytdl":
                    ytdl_media = "video"
                elif self.video and (url := self._extract_video(post)):
                    yield Message.Url, url, post
                if self.cover and (url := self._extract_cover(post, "video")):
                    yield Message.Url, url, post

            else:
                self.log.info("%s: Skipping post", tiktok_url)

            if ytdl_media:
                if not original_title:
                    title = f"TikTok {ytdl_media} #{post['id']}"
                post.update({
                    "type"      : ytdl_media,
                    "image"     : None,
                    "filename"  : "",
                    "extension" : "mp3" if ytdl_media == "audio" else "mp4",
                    "title"     : title,
                    "num"       : 0,
                    "img_id"    : "",
                    "width"     : 0,
                    "height"    : 0,
                })
                yield Message.Url, "ytdl:" + tiktok_url, post

    def _sanitize_url(self, url):
        return text.ensure_http_scheme(url.replace("/photo/", "/video/", 1))

    def _extract_rehydration_data(self, url, additional_keys=[]):
        tries = 0
        while True:
            try:
                response = self.request(url)
                if response.history and "/login" in response.url:
                    raise exception.AuthorizationError(
                        "HTTP redirect to login page "
                        f"('{response.url.partition('?')[0]}')")
                html = response.text
                data = text.extr(
                    html, '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" '
                    'type="application/json">', '</script>')
                data = util.json_loads(data)["__DEFAULT_SCOPE__"]
                for key in additional_keys:
                    data = data[key]
                return data
            except (ValueError, KeyError):
                # We failed to retrieve rehydration data. This happens
                # relatively frequently when making many requests, so
                # retry.
                if tries >= self._retries:
                    raise
                tries += 1
                self.log.warning("%s: Failed to retrieve rehydration data "
                                 "(%s/%s)", url.rpartition("/")[2], tries,
                                 self._retries)
                self.sleep(self._timeout, "retry")

    def _extract_video(self, post):
        video = post["video"]
        try:
            url = video["playAddr"]
        except KeyError:
            raise exception.ExtractionError("Failed to extract video URL, you "
                                            "may need cookies to continue")
        text.nameext_from_url(url, post)
        post.update({
            "type"     : "video",
            "image"    : None,
            "title"    : post["desc"] or f"TikTok video #{post['id']}",
            "duration" : video.get("duration"),
            "num"      : 0,
            "img_id"   : "",
            "audio_id" : "",
            "width"    : video.get("width"),
            "height"   : video.get("height"),
        })
        if not post["extension"]:
            post["extension"] = video.get("format", "mp4")
        return url

    def _extract_audio(self, post):
        audio = post["music"]
        url = audio["playUrl"]
        text.nameext_from_url(url, post)
        post.update({
            "type"     : "audio",
            "image"    : None,
            "title"    : post["desc"] or f"TikTok audio #{post['id']}",
            "duration" : audio.get("duration"),
            "num"      : 0,
            "img_id"   : "",
            "audio_id" : audio.get("id"),
            "width"    : 0,
            "height"   : 0,
        })
        if not post["extension"]:
            post["extension"] = "mp3"
        return url

    def _extract_cover(self, post, type):
        media = post[type]

        for cover_id in ("thumbnail", "cover", "originCover", "dynamicCover"):
            if url := media.get(cover_id):
                break
        else:
            return

        text.nameext_from_url(url, post)
        post.update({
            "type"     : "cover",
            "extension": "jpg",
            "image"    : url,
            "title"    : post["desc"] or f"TikTok {type} cover #{post['id']}",
            "duration" : media.get("duration"),
            "num"      : 0,
            "img_id"   : "",
            "cover_id" : cover_id,
            "width"    : 0,
            "height"   : 0,
        })
        return url

    def _check_status_code(self, detail, url, type_of_url):
        status = detail.get("statusCode")
        if not status:
            return True

        if status == 10222:
            self.log.error("%s: Login required to access this %s", url,
                           type_of_url)
        elif status == 10204:
            self.log.error("%s: Requested %s not available", url, type_of_url)
        elif status == 10231:
            self.log.error("%s: Region locked - Try downloading with a "
                           "VPN/proxy connection", url)
        else:
            self.log.error(
                "%s: Received unknown error code %s ('%s')",
                url, status, detail.get("statusMsg") or "")
        return False


class TiktokPostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok link"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:@([\w_.-]*)|share)/(?:phot|vide)o/(\d+)"
    example = "https://www.tiktok.com/@USER/photo/1234567890"

    def urls(self):
        user, post_id = self.groups
        url = f"{self.root}/@{user or ''}/video/{post_id}"
        return (url,)


class TiktokVmpostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok VM link"""
    subcategory = "vmpost"
    pattern = (r"(?:https?://)?(?:"
               r"(?:v[mt]\.)?tiktok\.com|(?:www\.)?tiktok\.com/t"
               r")/(?!@)([^/?#]+)")
    example = "https://vm.tiktok.com/1a2B3c4E5"

    def items(self):
        url = text.ensure_http_scheme(self.url)
        headers = {"User-Agent": "facebookexternalhit/1.1"}

        url = self.request_location(url, headers=headers, notfound="post")
        if not url or len(url) <= 28:
            # https://www.tiktok.com/?_r=1
            raise exception.NotFoundError("post")

        data = {"_extractor": TiktokPostExtractor}
        yield Message.Queue, url.partition("?")[0], data


class TiktokUserExtractor(TiktokExtractor):
    """Extract a TikTok user's profile"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/@([\w_.-]+)/?(?:$|\?|#)"
    example = "https://www.tiktok.com/@USER"

    def _init(self):
        super()._init()
        self.avatar = self.config("avatar", True)
        self.photo = self.config("photos", True)
        # If set to "ytdl", we shall first go via yt-dlp. If that fails,
        # we shall attempt to extract directly.
        self.ytdl = self.config("tiktok-user-extractor") == "ytdl"
        self.range = self.config("tiktok-range")
        if self.range is None or not self.range and self.range != 0:
            self.range = ""

    def items(self):
        """Attempt to [use yt-dlp/youtube-dl to] extract links from a
        user's page"""

        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"
        rehydration_data = None

        if self.avatar:
            try:
                rehydration_data = self._extract_user_rehydration_data(
                    profile_url)
                avatar_url, avatar = self._generate_avatar(
                    user_name, rehydration_data)
            except Exception as exc:
                self.log.warning("Unable to extract 'avatar' URL (%s: %s)",
                                 exc.__class__.__name__, exc)
            else:
                yield Message.Directory, "", avatar
                yield Message.Url, avatar_url, avatar

        entries = []
        if self.ytdl:
            entries = self._extract_entries_via_ytdl(profile_url)
            if not entries:
                self.log.warning(f"Could not extract TikTok user {user_name} "
                                 "via yt-dlp or youtube-dl, attempting the "
                                 "extraction directly")
        if not entries:
            entries = self._extract_entries(profile_url, user_name,
                                            rehydration_data)
            if not entries:
                self.log.warning("Could not extract any video or photo "
                                 f"entries from TikTok user {user_name}, "
                                 "try extracting user information using "
                                 "yt-dlp using the -o "
                                 "tiktok-user-extractor=ytdl argument")

        for video in entries:
            data = {"_extractor": TiktokPostExtractor}
            yield Message.Queue, video, data

    def _extract_user_rehydration_data(self, profile_url):
        return self._extract_rehydration_data(profile_url,
                                              ["webapp.user-detail"])

    def _generate_avatar(self, user_name, data):
        data = data["userInfo"]["user"]
        data["user"] = user_name
        avatar_url = data["avatarLarger"]
        avatar = text.nameext_from_url(avatar_url, data.copy())
        avatar.update({
            "type"  : "avatar",
            "title" : "@" + user_name,
            "id"    : data["id"],
            "img_id": avatar["filename"].partition("~")[0],
            "num"   : 0,
        })
        return (avatar_url, avatar)

    def _extract_entries_via_ytdl(self, profile_url):
        try:
            module = ytdl.import_module(self.config("module"))
        except (ImportError, SyntaxError) as exc:
            self.log.error("Cannot import module '%s'",
                           getattr(exc, "name", ""))
            self.log.traceback(exc)
            return False

        extr_opts = {
            "extract_flat"           : True,
            "ignore_no_formats_error": True,
        }
        user_opts = {
            "retries"                : self._retries,
            "socket_timeout"         : self._timeout,
            "nocheckcertificate"     : not self._verify,
            "playlist_items"         : str(self.range),
        }
        if self._proxies:
            user_opts["proxy"] = self._proxies.get("http")

        ytdl_instance = ytdl.construct_YoutubeDL(
            module, self, user_opts, extr_opts)

        # Transfer cookies to ytdl.
        if self.cookies:
            set_cookie = ytdl_instance.cookiejar.set_cookie
            for cookie in self.cookies:
                set_cookie(cookie)

        with ytdl_instance as ydl:
            info_dict = ydl._YoutubeDL__extract_info(
                profile_url, ydl.get_info_extractor("TikTokUser"),
                False, {}, True)
            # This should be a list of video and photo post URLs in /video/
            # format.
            return [video["url"].partition("?")[0]
                    for video in info_dict["entries"]]

    def _extract_entries(self, profile_url, user_name, data):
        # First, we need to extract the secUid of the user.
        sec_uid, fail_early = self._extract_sec_uid(profile_url, user_name,
                                                    data)
        if not sec_uid:
            raise exception.ExtractionError(
                f"{user_name}: unable to extract secondary user ID, or this "
                "user has no posts")

        # Once we've extracted the secondary user ID, we can begin extracting
        # item lists of the user.
        seen_ids = set()
        item_details = {}
        device_id = str(randint(7250000000000000000, 7325099899999994577))
        cursor = int(time() * 1e3)

        def generate_urls():
            with open("debug-2.json", mode="w", encoding="utf-8") as f:
                f.write(util.json_dumps(item_details))
            return [f"{profile_url}/video/{id}"
                    for id in reversed(sorted(seen_ids))
                    if self._matches_filters(item_details.get(id))]

        for page in count(start=1):
            self.log.info("%s: retrieving page %d", profile_url, page)
            tries = 0
            while True:
                try:
                    url = self._build_api_request_url(cursor, device_id,
                                                      sec_uid)
                    response = self.request(url)
                    data = util.json_loads(response.text)
                    ids = set([item["id"] for item in data["itemList"]])
                    if seen_ids and len(ids.difference(seen_ids)) == 0:
                        # TikTok API keeps sending the same page/s, likely due
                        # to a bad device ID. Generate a new one and try again.
                        device_id = str(randint(7250000000000000000,
                                                7325099899999994577))
                        self.log.warning("%s: TikTok API keeps sending the "
                                         "same page. Taking measures to avoid "
                                         "an infinite loop", profile_url)
                        raise exception.ExtractionError(
                            "TikTok API keeps sending the same page")
                    seen_ids = seen_ids.union(ids)
                    incoming_item_details = dict(
                        (item["id"], item) for item in data["itemList"])
                    item_details = dict(item_details, **incoming_item_details)

                    old_cursor = cursor
                    cursor = int(data["itemList"][-1]["createTime"]) * 1e3
                    if not cursor or old_cursor == cursor:
                        # User may not have posted within this ~1 week look
                        # back, so manually adjust cursor.
                        cursor = old_cursor - 7 * 86_400_000
                    # In case 'hasMorePrevious' is wrong, break if we have gone
                    # back before TikTok existed.
                    has_more_previous = data.get("hasMorePrevious")
                    if cursor < 1472706000000 or not has_more_previous:
                        return generate_urls()

                    # This code path is ideally only reached when one of the
                    # following is true:
                    # 1. TikTok profile is private and webpage detection was
                    #    bypassed due to a profile URL containing a sec_uid.
                    # 2. TikTok profile is *not* private but all of their
                    #    videos are private.
                    if fail_early and not seen_ids:
                        self.log.error("%s: this user's account is likely "
                                       "either private or all of their videos "
                                       "are private. Log into an account that "
                                       "has access", profile_url)
                        return generate_urls()

                    # Continue to next page and reset retry counter.
                    break
                except Exception:
                    if tries >= self._retries:
                        raise
                    tries += 1
                    self.log.warning("%s: Failed to retrieve page %d (%s/%s)",
                                     url, page, tries, self._retries)
                    self.sleep(self._timeout, "retry")

    def _extract_sec_uid(self, profile_url, user_name, data):
        sec_uid, fail_early = None, False
        if fullmatch(SEC_UID_PATTERN, user_name):
            # If it was provided in the URL, then we can skip this step.
            sec_uid = user_name
            fail_early = True
        else:
            if not data:
                # If we haven't extracted rehydration data yet, do so now.
                data = self._extract_user_rehydration_data(profile_url)
            # Video count workaround ported from yt-dlp: sometimes TikTok
            # reports a profile as private even though we have the cookies to
            # access it. We know that we can access it if we can see the videos
            # stats. If we can't, we assume that we don't have access to the
            # profile.
            user_info = data["userInfo"]
            if "stats" not in user_info:
                video_count = user_info["statsV2"]["videoCount"]
            else:
                video_count = user_info["stats"]["videoCount"]
            video_count = int(video_count)
            if not video_count:
                if self._check_status_code(data, profile_url, "profile"):
                    self.log.warning("%s: This profile has no known posts",
                                     profile_url)
                return sec_uid, fail_early
            sec_uid = str(user_info["user"]["secUid"])
            fail_early = not user_info.get("itemList")
        return sec_uid, fail_early

    def _build_api_request_url(self, cursor, device_id, sec_uid):
        verify_fp = f"verify_{''.join(choices(hexdigits, k=7))}"
        query_parameters = {
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "Win32",
            "browser_version": "5.0+(Windows)",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "count": "15",
            # We must not write this as a floating-point number:
            "cursor": f"{floor(cursor)}",
            "device_id": f"{device_id}",
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": "2",
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": "en",
            "os": "windows",
            "priority_region": "",
            "referer": "",
            "region": "US",
            "screen_height": "1080",
            "screen_width": "1920",
            "secUid": f"{sec_uid}",
            # Pagination type: 0 == oldest-to-newest, 1 == newest-to-oldest.
            "type": "1",
            "tz_name": "UTC",
            "verifyFp": verify_fp,
            "webcast_language": "en",
        }
        query_string = "&".join([f"{name}={quote(value, safe='+')}"
                                 for name, value in query_parameters.items()])
        return f"https://www.tiktok.com/api/creator/item_list/?{query_string}"

    def _matches_filters(self, item):
        if not item:
            return True
        is_image_post = "imagePost" in item
        if not self.photo and is_image_post:
            return False
        if not self.video and not is_image_post:
            return False
        return True
