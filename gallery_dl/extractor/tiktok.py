# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tiktok.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, ytdl, exception
import functools
import itertools
import random
import time

BASE_PATTERN = r"(?:https?://)?(?:www\.)?tiktokv?\.com"
USER_PATTERN = BASE_PATTERN + r"/@([\w_.-]+)"


class TiktokExtractor(Extractor):
    """Base class for TikTok extractors"""
    category = "tiktok"
    directory_fmt = ("{category}", "{user}")
    filename_fmt = (
        "{id}{num:?_//>02} {title[b:150]}{file_id:? [/]/}.{extension}")
    archive_fmt = "{id}_{num}_{file_id}"
    root = "https://www.tiktok.com"
    cookies_domain = ".tiktok.com"
    rehydration_data_cache = {}
    rehydration_data_app_context_cache = {}

    def _init(self):
        self.photo = self.config("photos", True)
        self.audio = self.config("audio", True)
        self.video = self.config("videos", True)
        self.cover = self.config("covers", False)

        self.range = self.config("tiktok-range") or ""
        self.range_predicate = util.RangePredicate(self.range)

    def items(self):
        for tiktok_url in self.posts():
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
            post["post_type"] = "image" if "imagePost" in post else "video"
            original_title = title = post["desc"]

            yield Message.Directory, "", post
            ytdl_media = False

            if "imagePost" in post:
                if self.photo:
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
                            "file_id": post["filename"].partition("~")[0],
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
                    "file_id"   : "",
                    "width"     : 0,
                    "height"    : 0,
                })
                yield Message.Url, "ytdl:" + tiktok_url, post

    def _sanitize_url(self, url):
        return text.ensure_http_scheme(url.replace("/photo/", "/video/", 1))

    def _extract_rehydration_data(self, url, additional_keys=[], *,
                                  has_keys=[]):
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
                for assert_key in has_keys:
                    if assert_key not in data:
                        raise KeyError(assert_key)
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

    def _extract_rehydration_data_user(self, profile_url, additional_keys=()):
        if profile_url in self.rehydration_data_cache:
            data = self.rehydration_data_cache[profile_url]
        else:
            data = self._extract_rehydration_data(
                profile_url,
                has_keys=["webapp.user-detail", "webapp.app-context"]
            )
            self.rehydration_data_cache[profile_url] = \
                data["webapp.user-detail"]
            self.rehydration_data_app_context_cache = \
                data["webapp.app-context"]
            data = data["webapp.user-detail"]
        if not self._check_status_code(data, profile_url, "profile"):
            raise exception.ExtractionError(
                "%s: could not extract rehydration data", profile_url)
        try:
            for key in additional_keys:
                data = data[key]
        except KeyError as exc:
            self.log.traceback(exc)
            raise exception.ExtractionError(
                "%s: could not extract rehydration data (%s)",
                profile_url, ", ".join(additional_keys))
        return data

    def _ensure_rehydration_data_app_context_cache_is_populated(self):
        if not self.rehydration_data_app_context_cache:
            self.rehydration_data_app_context_cache = \
                self._extract_rehydration_data_user(
                    "https://www.tiktok.com/", ["webapp.app-context"])

    def _extract_sec_uid(self, profile_url, user_name):
        sec_uid = self._extract_id(
            profile_url, user_name, r"MS4wLjABAAAA[\w-]{64}", "secUid")
        if sec_uid is None:
            raise exception.AbortExtraction(
                f"{user_name}: unable to extract secondary user ID")
        return sec_uid

    def _extract_author_id(self, profile_url, user_name):
        author_id = self._extract_id(
            profile_url, user_name, r"[0-9]+", "id")
        if author_id is None:
            raise exception.AbortExtraction(
                f"{user_name}: unable to extract user ID")
        return author_id

    def _extract_id(self, profile_url, user_name, regex, id_key):
        match = text.re(regex).fullmatch

        if match(user_name) is not None:
            # If it was provided in the URL, then we can skip extracting it
            # from the rehydration data.
            return user_name

        id = self._extract_rehydration_data_user(
            profile_url, ("userInfo", "user", id_key))
        return None if match(id) is None else id

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
            "file_id"  : video.get("id"),
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
            "file_id"  : audio.get("id"),
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
            "file_id"  : cover_id,
            "width"    : 0,
            "height"   : 0,
        })
        return url

    def _check_status_code(self, detail, url, type_of_url):
        status = detail.get("statusCode")
        if not status:
            return True

        if status == 10222:
            # Video count workaround ported from yt-dlp: sometimes TikTok
            # reports a profile as private even though we have the cookies to
            # access it. We know that we can access it if we can see the
            # videos stats. If we can't, we assume that we don't have access
            # to the profile.
            # We only care about this workaround for webapp.user-detail
            # objects, so always fail the workaround for e.g.
            # webapp.video-detail objects.
            video_count = self._extract_video_count_from_user_detail(detail)
            if video_count is None:
                self.log.error("%s: Login required to access this %s", url,
                               type_of_url)
            elif video_count > 0:
                return True
            else:
                self.log.error("%s: Login required to access this %s, or this "
                               "profile has no videos posted", url,
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

    def _extract_video_count_from_user_detail(self, detail):
        user_info = detail.get("userInfo")
        if not user_info:
            return None
        stats = user_info.get("stats") or user_info.get("statsV2")
        try:
            # stats.videoCount is an int, but statsV2.videoCount is a
            # string, so we must explicitly convert the attribute.
            return int(stats["videoCount"])
        except (KeyError, ValueError):
            return None


class TiktokPostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok link"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:@([\w_.-]*)|share)/(?:phot|vide)o/(\d+)"
    example = "https://www.tiktok.com/@USER/photo/1234567890"

    def posts(self):
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


class TiktokUserExtractor(Dispatch, TiktokExtractor):
    """Extractor for a TikTok user profile"""
    pattern = USER_PATTERN + r"/?(?:$|\?|#)"
    example = "https://www.tiktok.com/@USER"

    def items(self):
        base = f"{self.root}/@{self.groups[0]}/"
        return self._dispatch_extractors((
            (TiktokAvatarExtractor , base + "avatar"),
            (TiktokPostsExtractor  , base + "posts"),
            (TiktokRepostsExtractor, base + "reposts"),
            (TiktokStoriesExtractor, base + "stories"),
            (TiktokLikesExtractor  , base + "likes"),
            (TiktokSavedExtractor  , base + "saved"),
        ), ("avatar", "posts"))


class TiktokAvatarExtractor(TiktokExtractor):
    subcategory = "avatar"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.tiktok.com/@USER/avatar"

    def items(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        data = self._extract_rehydration_data_user(
            profile_url, ("userInfo", "user"))
        data["user"] = data.get("uniqueId", user_name)
        avatar_url = data.get("avatarLarger") or data.get("avatarMedium") \
            or data["avatarThumb"]
        avatar = text.nameext_from_url(avatar_url, data.copy())
        avatar.update({
            "type"   : "avatar",
            "title"  : "@" + data["user"],
            "id"     : data["id"],
            "file_id": avatar["filename"].partition("~")[0],
            "num"    : 0,
        })

        yield Message.Directory, "", avatar
        yield Message.Url, avatar_url, avatar


class TiktokPostsExtractor(TiktokExtractor):
    subcategory = "posts"
    pattern = USER_PATTERN + r"/posts"
    example = "https://www.tiktok.com/@USER/posts"

    def posts(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"
        self.user_provided_cookies = bool(self.cookies)

        # If set to "ytdl", we shall first go via yt-dlp. If that fails,
        # we shall attempt to extract directly.
        if self.config("ytdl", False):
            if posts := self._extract_posts_ytdl(profile_url):
                return posts
            ytdl = True
            self.log.warning("Could not extract TikTok user "
                             f"{user_name} via yt-dlp or youtube-dl, "
                             "attempting the extraction directly")
        else:
            ytdl = False

        if posts := self._extract_posts_api(profile_url, user_name):
            return posts

        message = "Could not extract any posts from TikTok user " \
                  f"{user_name}"
        if not ytdl:
            message += ", try extracting post information using " \
                       "yt-dlp with the -o " \
                       "tiktok-user-extractor=ytdl argument"
        self.log.warning(message)
        return ()

    def _extract_posts_ytdl(self, profile_url):
        try:
            module = ytdl.import_module(self.config("module"))
        except (ImportError, SyntaxError) as exc:
            self.log.error("Cannot import module '%s'",
                           getattr(exc, "name", ""))
            self.log.traceback(exc)
            return []

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

    def _extract_posts_api(self, profile_url, user_name):
        self.post_order = self.config("order-posts") or "desc"
        if self.post_order not in ["desc", "asc", "reverse", "popular"]:
            self.post_order = "desc"

        sec_uid = self._extract_sec_uid(profile_url, user_name)
        if not self.user_provided_cookies:
            if self.post_order != "desc":
                self.log.warning(
                    "%s: no cookies have been provided so the order-posts "
                    "option will not take effect. You must provide cookies in "
                    "order to extract a profile's posts in non-descending "
                    "order",
                    profile_url
                )
            return self._extract_posts_api_legacy(
                profile_url, sec_uid, self.range_predicate)
        try:
            return self._extract_posts_api_order(
                profile_url, sec_uid, self.range_predicate)
        except Exception as exc:
            self.log.error(
                "%s: failed to extract user posts using post/item_list (make "
                "sure you provide valid cookies). Attempting with legacy "
                "creator/item_list endpoint that does not support post "
                "ordering",
                profile_url
            )
            self.log.traceback(exc)
            return self._extract_posts_api_legacy(
                profile_url, sec_uid, self.range_predicate)

    def _extract_posts_api_order(self, profile_url, sec_uid, range_predicate):
        post_item_list_request_type = "0"
        if self.post_order in ["asc", "reverse"]:
            post_item_list_request_type = "2"
        elif self.post_order in ["popular"]:
            post_item_list_request_type = "1"
        query_parameters = {
            "secUid": sec_uid,
            "post_item_list_request_type": post_item_list_request_type,
            "count": "15",
            "needPinnedItemIds": "false",
        }
        request = TiktokPostItemListRequest(range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)

    def _extract_posts_api_legacy(self, profile_url, sec_uid, range_predicate):
        query_parameters = {
            "secUid": sec_uid,
            "type": "1",
            "count": "15",
        }
        request = TiktokCreatorItemListRequest(range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)


class TiktokRepostsExtractor(TiktokExtractor):
    subcategory = "reposts"
    pattern = USER_PATTERN + r"/reposts"
    example = "https://www.tiktok.com/@USER/reposts"

    def posts(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        query_parameters = {
            "secUid": self._extract_sec_uid(profile_url, user_name),
            "post_item_list_request_type": "0",
            "needPinnedItemIds": "false",
            "count": "15",
        }
        request = TiktokRepostItemListRequest(self.range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)


class TiktokStoriesExtractor(TiktokExtractor):
    subcategory = "stories"
    pattern = USER_PATTERN + r"/stories"
    example = "https://www.tiktok.com/@USER/stories"

    def posts(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        query_parameters = {
            "authorId": self._extract_author_id(profile_url, user_name),
            "loadBackward": "false",
            "count": "5",
        }
        request = TiktokStoryItemListRequest()
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)


class TiktokLikesExtractor(TiktokExtractor):
    subcategory = "likes"
    pattern = USER_PATTERN + r"/like[sd]"
    example = "https://www.tiktok.com/@USER/liked"

    def posts(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        query_parameters = {
            "secUid": self._extract_sec_uid(profile_url, user_name),
            "post_item_list_request_type": "0",
            "needPinnedItemIds": "false",
            "count": "15",
        }
        request = TiktokFavoriteItemListRequest(self.range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)


class TiktokSavedExtractor(TiktokExtractor):
    subcategory = "saved"
    pattern = USER_PATTERN + r"/saved"
    example = "https://www.tiktok.com/@USER/saved"

    def posts(self):
        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        query_parameters = {
            "secUid": self._extract_sec_uid(profile_url, user_name),
            "post_item_list_request_type": "0",
            "needPinnedItemIds": "false",
            "count": "15",
        }
        request = TiktokSavedPostItemListRequest(self.range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)


class TiktokFollowingExtractor(TiktokUserExtractor):
    """Extract all of the stories of all of the users you follow"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/following"
    example = "https://www.tiktok.com/following"

    def items(self):
        """Attempt to extract all of the stories of all of the accounts
        the user follows"""

        query_parameters = {
            "storyFeedScene": "3",
            "count": "15",
        }
        request = TiktokStoryUserListRequest()
        if not request.execute(self, self.url, query_parameters):
            self.log.error("%s: could not extract follower list, make sure "
                           "you are using logged-in cookies", self.url)
        users = request.generate_urls()
        if len(users) == 0:
            self.log.warning("%s: No followers with stories could be "
                             "extracted", self.url)

        entries = []
        # Batch all of the users up into groups of at most ten and use the
        # batch endpoint to improve performance. The response to the story user
        # list request may also include the user themselves, so skip them if
        # they ever turn up.
        for b in range((len(users) - 1) // 10 + 1):
            batch_number = b + 1
            user_batch = users[b*10:batch_number*10]

            # Handle edge case where final batch is composed of a single user
            # and that user is the one we need to skip. If we don't handle this
            # here (or when we generate the author ID list later), we will
            # trigger an AssertionError for an empty author ID list.
            if len(user_batch) == 1:
                if self._is_current_user(user_batch[0][0]):
                    continue

            self.log.info("TikTok user stories, batch %d: %s", batch_number,
                          ", ".join([profile_url for user_id, profile_url in
                                     user_batch if not self._is_current_user(
                                         user_id)]))

            # Since we've already extracted all of the author IDs, we should be
            # able to avoid having to request rehydration data (except for one
            # time, since it's required to make _is_current_user() work), but
            # we should keep this mechanism in place for safety.
            author_ids = [self._extract_author_id(profile_url, user_id)
                          for user_id, profile_url in user_batch
                          if not self._is_current_user(user_id)]
            query_parameters = {
                "authorIds": ",".join(author_ids),
                "storyCallScene": "2",
            }
            request = TiktokStoryBatchItemListRequest()
            request.execute(self, f"Batch {batch_number}", query_parameters)
            # We technically don't need to have the correct user name in the
            # URL and it's easier to just ignore it here.
            entries += request.generate_urls("https://www.tiktok.com/@_",
                                             self.video, self.photo,
                                             self.audio)

        for video in entries:
            data = {"_extractor": TiktokPostExtractor}
            yield Message.Queue, video, data

    def _is_current_user(self, user_id):
        self._ensure_rehydration_data_app_context_cache_is_populated()
        if "user" not in self.rehydration_data_app_context_cache:
            return False
        if "uid" not in self.rehydration_data_app_context_cache["user"]:
            return False
        return self.rehydration_data_app_context_cache["user"]["uid"] == \
            user_id


class TiktokPaginationCursor:
    def current_page(self):
        """Must return the page the cursor is currently pointing to.

        Returns
        -------
        int
            The current value of the cursor.
        """

        return 0

    def next_page(self, data, query_parameters):
        """Must progress the cursor to the next page.

        Parameters
        ----------
        data : dict
            The response of the most recent request.
        query_parameters : dict
            All of the query parameters used for the most recent
            request.

        Returns
        -------
        bool
            True if the cursor detects that we've reached the end, False
            otherwise.
        """

        return True


class TiktokTimeCursor(TiktokPaginationCursor):
    def __init__(self, *, reverse=True):
        super().__init__()
        self.cursor = 0
        # If we expect the cursor to go up or down as we go to the next page.
        # True for down, False for up.
        self.reverse = reverse

    def current_page(self):
        return self.cursor

    def next_page(self, data, query_parameters):
        skip_fallback_logic = self.cursor == 0
        new_cursor = int(data.get("cursor", 0))
        no_cursor = not new_cursor
        if not skip_fallback_logic:
            # If the new cursor doesn't go in the direction we expect, use the
            # fallback logic instead.
            if self.reverse and (new_cursor > self.cursor or no_cursor):
                new_cursor = self.fallback_cursor(data)
            elif not self.reverse and (new_cursor < self.cursor or no_cursor):
                new_cursor = self.fallback_cursor(data)
        elif no_cursor:
            raise exception.ExtractionError("Could not extract next cursor")
        self.cursor = new_cursor
        return not data.get("hasMore", False)

    def fallback_cursor(self, data):
        try:
            return int(data["itemList"][-1]["createTime"]) * 1000
        except Exception:
            return 7 * 86_400_000 * (-1 if self.reverse else 1)


class TiktokForwardTimeCursor(TiktokTimeCursor):
    def __init__(self):
        super().__init__(reverse=False)


class TiktokBackwardTimeCursor(TiktokTimeCursor):
    def __init__(self):
        super().__init__(reverse=True)


class TiktokPopularTimeCursor(TiktokTimeCursor):
    def __init__(self):
        super().__init__(reverse=True)

    def fallback_cursor(self, data):
        # Don't really know what to do here, all I know is that the cursor
        # for the popular item feed goes down and it does not appear to be
        # based on item list timestamps at all.
        return -50_000


class TiktokLegacyTimeCursor(TiktokPaginationCursor):
    def __init__(self):
        super().__init__()
        self.cursor = int(time.time()) * 1000

    def current_page(self):
        return self.cursor

    def next_page(self, data, query_parameters):
        old_cursor = self.cursor
        try:
            self.cursor = int(data["itemList"][-1]["createTime"]) * 1000
        except Exception:
            self.cursor = 0
        if not self.cursor or old_cursor == self.cursor:
            # User may not have posted within this ~1 week look back,
            # so manually adjust the cursor.
            self.cursor = old_cursor - 7 * 86_400_000
        # In case 'hasMorePrevious' is wrong, break if we have
        # gone back before TikTok existed.
        has_more_previous = data.get("hasMorePrevious")
        return self.cursor < 1472706000000 or not has_more_previous


class TiktokItemCursor(TiktokPaginationCursor):
    def __init__(self, list_key: str = "itemList"):
        super().__init__()
        self.cursor = 0
        self.list_key = list_key

    def current_page(self):
        return self.cursor

    def next_page(self, data, query_parameters):
        # We should offset the cursor by the number of items in the response.
        # Sometimes less items are returned than what was requested in the
        # count parameter! We could fall back onto the count query parameter
        # but we could miss out on some posts, and truth is if the expected
        # item list isn't in the response, the extraction was going to fail
        # anyway.
        self.cursor += len(data[self.list_key])
        return not data.get("hasMore", False)


class TiktokPaginationRequest:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._regenerate_device_id()
        self.items = {}

    def execute(self, extractor, url, query_parameters):
        """Performs requests until all pages have been retrieved.

        The items retrieved from this request are stored in self.items.
        Each call to execute() will clear the previous value of
        self.items.

        Usually extractors want a simple list of URLs. For this, each
        request subtype is to implement generate_urls().

        Parameters
        ----------
        extractor : TiktokExtractor
            The TikTok extractor performing the request.
        url : str
            The URL associated with this request for logging purposes.
        query_parameters : dict[str, str]
            The query parameters to apply to this request.

        Returns
        -------
        bool
            True if the request was performed successfully and all items
            were retrieved, False if no items or only some items could
            be retrieved.
        """

        self.validate_query_parameters(query_parameters)
        self.items = {}
        cursor_type = self.cursor_type(query_parameters)
        cursor = cursor_type() if cursor_type else None
        for page in itertools.count(start=1):
            extractor.log.info("%s: retrieving %s page %d", url, self.endpoint,
                               page)
            tries = 0
            while True:
                try:
                    data, final_parameters = self._request_data(
                        extractor,
                        cursor,
                        query_parameters
                    )
                    incoming_items = self.extract_items(data)
                    self._detect_duplicate_pages(extractor, url,
                                                 set(self.items.keys()),
                                                 set(incoming_items.keys()))
                    self.items.update(incoming_items)
                    if cursor:
                        final_page_reached = cursor.next_page(data,
                                                              final_parameters)
                        exit_early = self.exit_early(extractor, url)
                        if exit_early or final_page_reached:
                            return True
                        # Continue to next page and reset tries counter.
                        break
                    else:
                        # This request has no cursor: return immediately.
                        return True
                except Exception as exc:
                    if tries >= extractor._retries:
                        extractor.log.error("%s: failed to retrieve %s page "
                                            "%d", url, self.endpoint, page)
                        extractor.log.traceback(exc)
                        return False
                    tries += 1
                    extractor.log.warning("%s: failed to retrieve %s page %d",
                                          url, self.endpoint, page)
                    extractor.sleep(extractor._timeout, "retry")

    def validate_query_parameters(self, query_parameters):
        """Used to validate the given parameters for this type of
        pagination request.

        For developer purposes only. You should call
        super().validate_query_parameters() for most requests as they
        will usually have a count parameter.

        Parameters
        ----------
        query_parameters : dict[str, str]
            The query parameters to validate.

        Raises
        -------
        AssertionError
            If mandatory query parameters are not given, or they are
            given in the wrong format.
        """

        assert "count" in query_parameters
        assert type(query_parameters["count"]) is str
        assert query_parameters["count"].isdigit()
        assert query_parameters["count"] != "0"

    def cursor_type(self, query_parameters):
        """Used to determine which type of cursor to use for this
        request, if any.

        Parameters
        ----------
        query_parameters : dict[str, str]
            The query parameters given to the execute() call.

        Returns
        -------
        Type[TiktokPaginationCursor] | None
            The type of cursor to use, if any.
        """

        return None

    def extract_items(self, data):
        """Used to extract data from the response of a request.

        Parameters
        ----------
        data : dict
            The data given by TikTok.

        Returns
        -------
        dict
            Each item from the response data, keyed on a unique ID.

        Raises
        ------
        Exception
            If items could not be extracted.
        """

        return {}

    def exit_early(self, extractor, url):
        """Used to determine if we should exit early from the request.

        You have access to the items extracted so far (self.items).

        Parameters
        ----------
        extractor : TiktokExtractor
            The extractor making the requests.
        url : str
            The URL associated with the executing request for logging
            purposes.

        Returns
        -------
        bool
            True if we should exit early, False otherwise.
        """

        return False

    def generate_urls(self):
        """Used to convert the items retrieved from the request into a
        list of URLs.

        Returns
        -------
        list
            Ideally one URL for each item, although subclasses are
            permitted to return a list of any format they wish.
        """

        return []

    def _regenerate_device_id(self):
        self.device_id = str(random.randint(
            7_250_000_000_000_000_000, 7_325_099_899_999_994_577))

    def _request_data(self, extractor, cursor, query_parameters):
        # Implement simple 1 retry mechanism without delays that handles the
        # flaky post/item_list endpoint.
        retries = 0
        while True:
            try:
                url, final_parameters = self._build_api_request_url(
                    cursor,
                    query_parameters
                )
                response = extractor.request(url)
                return (util.json_loads(response.text), final_parameters)
            except ValueError:
                if retries == 1:
                    raise
                extractor.log.warning(
                    "Could not decode response for this page, trying again"
                )
                retries += 1

    def _build_api_request_url(self, cursor, extra_parameters):
        query_parameters = {
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "Win32",
            "browser_version": "5.0 (Windows)",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": self.device_id,
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
            "tz_name": "UTC",
            "verifyFp": "verify_" + "".join(random.choices(
                "0123456789abcdef", k=7)),
            "webcast_language": "en",
        }
        if cursor:
            # We must not write this as a floating-point number:
            query_parameters["cursor"] = str(int(cursor.current_page()))
        for key, value in extra_parameters.items():
            query_parameters[key] = f"{value}"
        query_str = text.build_query(query_parameters)
        return (f"https://www.tiktok.com/api/{self.endpoint}/?{query_str}",
                query_parameters)

    def _detect_duplicate_pages(self, extractor, url, seen_ids, incoming_ids):
        if incoming_ids and incoming_ids == seen_ids:
            # TikTok API keeps sending the same page, likely due to
            # a bad device ID. Generate a new one and try again.
            self._regenerate_device_id()
            extractor.log.warning("%s: TikTok API keeps sending the same "
                                  "page. Taking measures to avoid an infinite "
                                  "loop", url)
            raise exception.ExtractionError(
                "TikTok API keeps sending the same page")


class TiktokItemListRequest(TiktokPaginationRequest):
    def __init__(self, endpoint, type_of_items, range_predicate):
        super().__init__(endpoint)
        self.type_of_items = type_of_items
        self.range_predicate = range_predicate
        self.exit_early_due_to_no_items = False

    def extract_items(self, data):
        if "itemList" not in data:
            self.exit_early_due_to_no_items = True
            return {}
        return {item["id"]: item for item in data["itemList"]}

    def exit_early(self, extractor, url):
        if self.exit_early_due_to_no_items:
            extractor.log.warning("%s: could not extract any %s for this user",
                                  url, self.type_of_items)
            return True
        if not self.range_predicate:
            # No range predicate given.
            return False
        if len(self.range_predicate.ranges) == 0:
            # No range predicates given in the predicate object.
            return False
        # If our current selection of items can't satisfy the upper bound of
        # the predicate, we must continue extracting them until we can.
        return len(self.items) > self.range_predicate.upper

    def generate_urls(self, profile_url, video, photo, audio):
        urls = []
        for index, id in enumerate(self.items.keys()):
            if not self._matches_filters(self.items.get(id), index + 1, video,
                                         photo, audio):
                continue
            # Try to grab the author's unique ID, but don't cause the
            # extraction to fail if we can't, it's not imperative that the
            # URLs include the actual poster's unique ID.
            try:
                url = f"https://www.tiktok.com/@" \
                      f"{self.items[id]['author']['uniqueId']}/video/{id}"
            except KeyError:
                # Use the given profile URL as a back up.
                url = f"{profile_url}/video/{id}"
            urls.append(url)
        return urls

    def _matches_filters(self, item, index, video, photo, audio):
        # First, check if this index falls within any of our configured ranges.
        # If it doesn't, we filter it out.
        if self.range_predicate:
            range_match = len(self.range_predicate.ranges) == 0
            for range in self.range_predicate.ranges:
                if index in range:
                    range_match = True
                    break
            if not range_match:
                return False

        # Then, we apply basic video/photo filtering.
        if not item:
            return True
        is_image_post = "imagePost" in item
        if not photo and not audio and is_image_post:
            return False
        if not video and not is_image_post:
            return False
        return True


class TiktokCreatorItemListRequest(TiktokItemListRequest):
    """A less flaky version of the post/item_list endpoint that doesn't
    support latest/popular/oldest ordering."""

    def __init__(self, range_predicate):
        super().__init__("creator/item_list", "posts", range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "type" in query_parameters
        # Pagination type: 0 == oldest-to-newest, 1 == newest-to-oldest.
        # NOTE: ^ this type parameter doesn't seem to do what yt-dlp thinks it
        #       does. post/item_list is the only way to get an ordered feed
        #       based on latest/popular/oldest.
        assert query_parameters["type"] == "0" or \
            query_parameters["type"] == "1"

    def cursor_type(self, query_parameters):
        return TiktokLegacyTimeCursor


class TiktokPostItemListRequest(TiktokItemListRequest):
    """Retrieves posts in latest/popular/oldest ordering.

    Very often, this request will just return an empty response, making
    it quite flaky, but the next attempt to make the request usually
    does return a response. For this reason creator/item_list was kept
    as a backup, though it doesn't seem to support ordering.

    It also doesn't work without cookies.
    """

    def __init__(self, range_predicate):
        super().__init__("post/item_list", "posts", range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "post_item_list_request_type" in query_parameters
        # Pagination type:
        # 0 == newest-to-oldest.
        # 1 == popular.
        # 2 == oldest-to-newest.
        assert query_parameters["post_item_list_request_type"] in \
            ["0", "1", "2"]
        assert "needPinnedItemIds" in query_parameters
        # If this value is set to "true", and "post_item_list_request_type" is
        # set to "0", pinned posts will always show up first in the resulting
        # itemList. It keeps our logic simpler if we avoid this behavior by
        # setting this parameter to "false" (especially if we were to use a
        # really small "count" value like "1" or "2").
        assert query_parameters["needPinnedItemIds"] in ["false"]

    def cursor_type(self, query_parameters):
        request_type = query_parameters["post_item_list_request_type"]
        if request_type == "2":
            return TiktokForwardTimeCursor
        elif request_type == "1":
            return TiktokPopularTimeCursor
        else:
            return TiktokBackwardTimeCursor


class TiktokFavoriteItemListRequest(TiktokItemListRequest):
    """Retrieves a user's liked posts.

    Appears to only support descending order, but it can work without
    cookies.
    """

    def __init__(self, range_predicate):
        super().__init__("favorite/item_list", "liked posts", range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "post_item_list_request_type" in query_parameters
        assert query_parameters["post_item_list_request_type"] == "0"
        assert "needPinnedItemIds" in query_parameters
        assert query_parameters["needPinnedItemIds"] in ["false"]

    def cursor_type(self, query_parameters):
        return TiktokPopularTimeCursor


class TiktokRepostItemListRequest(TiktokItemListRequest):
    """Retrieves a user's reposts.

    Appears to only support descending order, but it can work without
    cookies.
    """

    def __init__(self, range_predicate):
        super().__init__("repost/item_list", "reposts", range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "post_item_list_request_type" in query_parameters
        assert query_parameters["post_item_list_request_type"] == "0"
        assert "needPinnedItemIds" in query_parameters
        assert query_parameters["needPinnedItemIds"] in ["false"]

    def cursor_type(self, query_parameters):
        return TiktokItemCursor


class TiktokSavedPostItemListRequest(TiktokItemListRequest):
    """Retrieves a user's saved posts.

    Appears to only support descending order, but it can work without
    cookies.
    """

    def __init__(self, range_predicate):
        super().__init__("user/collect/item_list", "saved posts",
                         range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "post_item_list_request_type" in query_parameters
        assert query_parameters["post_item_list_request_type"] == "0"
        assert "needPinnedItemIds" in query_parameters
        assert query_parameters["needPinnedItemIds"] in ["false"]

    def cursor_type(self, query_parameters):
        return TiktokPopularTimeCursor


class TiktokStoryItemListRequest(TiktokItemListRequest):
    def __init__(self):
        super().__init__("story/item_list", "stories", None)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "authorId" in query_parameters
        assert "loadBackward" in query_parameters
        assert query_parameters["loadBackward"] in ["true", "false"]

    def cursor_type(self, query_parameters):
        return TiktokItemCursor


class TiktokStoryBatchItemListRequest(TiktokItemListRequest):
    def __init__(self):
        super().__init__("story/batch/item_list", "stories", None)

    def validate_query_parameters(self, query_parameters):
        # This request type does not need a count parameter so don't invoke
        # super().validate_query_parameters().
        assert "authorIds" in query_parameters
        # I'd recommend between 1-10 users at a time, as that's what I see in
        # the webapp.
        author_count = query_parameters["authorIds"].count(",") + 1
        assert author_count >= 1 and author_count <= 10
        # Not sure what this parameter does.
        assert "storyCallScene" in query_parameters
        assert query_parameters["storyCallScene"] == "2"

    def extract_items(self, data):
        # We need to extract each itemList within the response and combine each
        # of them into a single list of items. If even one of the users doesn't
        # have an item list, "exit early," but continue to gather the rest
        # (this request doesn't use a cursor anyway so there is no concept of
        # exiting early).
        items = {}
        if type(data.get("batchStoryItemLists")) is not list:
            self.exit_early_due_to_no_items = True
            return items
        for userStories in data["batchStoryItemLists"]:
            items.update(super().extract_items(userStories))
        return items


class TiktokStoryUserListRequest(TiktokPaginationRequest):
    def __init__(self):
        super().__init__("story/user_list")
        self.exit_early_due_to_no_cookies = False

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        # Not sure what this parameter does.
        assert "storyFeedScene" in query_parameters
        assert query_parameters["storyFeedScene"] == "3"

    def cursor_type(self, query_parameters):
        return functools.partial(TiktokItemCursor, "storyUsers")

    def extract_items(self, data):
        if "storyUsers" not in data:
            self.exit_early_due_to_no_cookies = True
            return {}
        return {item["user"]["id"]: item["user"]["uniqueId"]
                for item in data["storyUsers"]}

    def exit_early(self, extractor, url):
        if self.exit_early_due_to_no_cookies:
            extractor.log.error("You must provide cookies to extract the "
                                "stories of your following list")
        return self.exit_early_due_to_no_cookies

    def generate_urls(self):
        return [(id, f"https://www.tiktok.com/@{name}")
                for id, name in self.items.items()]
