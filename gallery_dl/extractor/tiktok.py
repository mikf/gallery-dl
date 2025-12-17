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
AUTHOR_ID_PATTERN = r"[0-9]+"


# MARK: TiktokExtractor
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
        self.photo = self.config("photos", True)
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


# MARK: TiktokPostExtractor
class TiktokPostExtractor(TiktokExtractor):
    """Extract a single video or photo TikTok link"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:@([\w_.-]*)|share)/(?:phot|vide)o/(\d+)"
    example = "https://www.tiktok.com/@USER/photo/1234567890"

    def urls(self):
        user, post_id = self.groups
        url = f"{self.root}/@{user or ''}/video/{post_id}"
        return (url,)


# MARK: TiktokVmpostExtractor
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


# MARK: TiktokUserExtractor
class TiktokUserExtractor(TiktokExtractor):
    """Extract a TikTok user's profile"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/@([\w_.-]+)/?(?:$|\?|#)"
    example = "https://www.tiktok.com/@USER"

    def _init(self):
        super()._init()
        self.avatar = self.config("avatar", True)
        self.stories = self.config("stories", True)
        if type(self.stories) is str:
            self.stories = self.stories.lower()
        # If set to "ytdl", we shall first go via yt-dlp. If that fails,
        # we shall attempt to extract directly.
        self.ytdl = self.config("tiktok-user-extractor") == "ytdl"
        self.range = self.config("tiktok-range")
        if self.range is None or not self.range and self.range != 0:
            self.range = ""
        self.COUNT_QUERY_PARAMETER = 15
        self.rehydration_data_cache = {}
        self.rehydration_data_app_context_cache = {}

    # MARK: Overrides
    def items(self):
        """Attempt to [use yt-dlp/youtube-dl to] extract links from a
        user's page"""

        user_name = self.groups[0]
        profile_url = f"{self.root}/@{user_name}"

        if self.avatar:
            try:
                avatar_url, avatar = self._extract_avatar(profile_url,
                                                          user_name)
            except Exception as exc:
                self.log.warning("%s: unable to extract 'avatar' URL (%s: %s)",
                                 profile_url, exc.__class__.__name__, exc)
            else:
                yield Message.Directory, "", avatar
                yield Message.Url, avatar_url, avatar

        entries = []
        if self.stories != "only":
            if self.ytdl:
                entries = self._extract_posts_via_ytdl(profile_url)
                if not entries:
                    self.log.warning("Could not extract TikTok user "
                                     f"{user_name} via yt-dlp or youtube-dl, "
                                     "attempting the extraction directly")
            if not entries:
                entries = self._extract_posts(profile_url, user_name)
                if not entries:
                    message = "Could not extract any video or photo entries " \
                              f"from TikTok user {user_name}"
                    if not self.ytdl:
                        message += ", try extracting user information using " \
                                   "yt-dlp with the -o " \
                                   "tiktok-user-extractor=ytdl argument"
                    self.log.warning(message)

        if self.stories:
            entries += self._extract_stories(profile_url, user_name)
            if self.stories == "only" and not entries:
                self.log.warning(f"TikTok user {user_name} has no stories")

        for video in entries:
            data = {"_extractor": TiktokPostExtractor}
            yield Message.Queue, video, data

    def _extract_rehydration_data(self, profile_url, additional_keys=[]):
        if profile_url in self.rehydration_data_cache:
            data = self.rehydration_data_cache[profile_url]
        else:
            data = super()._extract_rehydration_data(
                profile_url,
                has_keys=["webapp.user-detail", "webapp.app-context"]
            )
            self.rehydration_data_cache[profile_url] = \
                data["webapp.user-detail"]
            self.rehydration_data_app_context_cache = \
                data["webapp.app-context"]
            data = data["webapp.user-detail"]
        if not self._check_status_code(data, profile_url, "profile"):
            raise exception.ExtractionError("%s: could not extract "
                                            "rehydration data", profile_url)
        try:
            for key in additional_keys:
                data = data[key]
        except KeyError as exc:
            self.log.traceback(exc)
            raise exception.ExtractionError("%s: could not extract "
                                            "rehydration data (%s)",
                                            profile_url,
                                            ", ".join(additional_keys))
        return data

    # MARK: Helpers
    def _extract_avatar(self, profile_url, user_name):
        data = self._extract_rehydration_data(
            profile_url, ["userInfo", "user"]
        ).copy()
        data["user"] = data.get("uniqueId", user_name)
        avatar_url = data.get("avatarLarger") or data.get("avatarMedium") \
            or data["avatarThumb"]
        avatar = text.nameext_from_url(avatar_url, data.copy())
        avatar.update({
            "type"   : "avatar",
            "title"  : "@" + data["user"],
            "id"     : data["id"],
            "img_id" : avatar["filename"].partition("~")[0],
            "num"    : 0,
        })
        return (avatar_url, avatar)

    def _extract_posts_via_ytdl(self, profile_url):
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

    def _extract_posts(self, profile_url, user_name):
        sec_uid = self._extract_sec_uid(profile_url, user_name)
        range_predicate = util.RangePredicate(self.range)
        query_parameters = {
            "secUid": sec_uid,
            "type": "1",
            "count": "15",
        }
        request = TiktokCreatorItemListRequest(range_predicate)
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)

    def _extract_stories(self, profile_url, user_name):
        author_id = self._extract_author_id(profile_url, user_name)
        query_parameters = {
            "authorId": author_id,
            "loadBackward": "false",
            "count": "5",
        }
        request = TiktokStoryItemListRequest()
        request.execute(self, profile_url, query_parameters)
        return request.generate_urls(profile_url, self.video, self.photo,
                                     self.audio)

    def _extract_sec_uid(self, profile_url, user_name):
        sec_uid = self._extract_id(profile_url, user_name, SEC_UID_PATTERN,
                                   "secUid")
        if not fullmatch(SEC_UID_PATTERN, sec_uid):
            raise exception.ExtractionError("%s: unable to extract secondary "
                                            "user ID", user_name)
        return sec_uid

    def _extract_author_id(self, profile_url, user_name):
        author_id = self._extract_id(profile_url, user_name, AUTHOR_ID_PATTERN,
                                     "id")
        if not fullmatch(AUTHOR_ID_PATTERN, author_id):
            raise exception.ExtractionError("%s: unable to extract user ID",
                                            user_name)
        return author_id

    def _extract_id(self, profile_url, user_name, regex, id_key):
        if fullmatch(regex, user_name):
            # If it was provided in the URL, then we can skip extracting it
            # from the rehydration data.
            return user_name
        else:
            return self._extract_rehydration_data(profile_url,
                                                  ["userInfo", "user", id_key])


# MARK: TiktokFollowingExtractor
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
        request.execute(self, self.url, query_parameters)
        users = request.generate_urls()
        if len(users) == 0:
            self.log.warning("No followers with stories could be extracted")

        entries = []
        # TODO: we could improve the performance of this using the
        #       /api/story/batch/item_list endpoint.
        for user_name, profile_url in users:
            if self._is_current_user(user_name):
                # The response to the story user list request may also include
                # the user themselves, so skip them if they turn up.
                continue
            entries += self._extract_stories(profile_url, user_name)

        for video in entries:
            data = {"_extractor": TiktokPostExtractor}
            yield Message.Queue, video, data

    def _is_current_user(self, user_name):
        if "user" not in self.rehydration_data_app_context_cache:
            return False
        if "uniqueId" not in self.rehydration_data_app_context_cache["user"]:
            return False
        return self.rehydration_data_app_context_cache["user"]["uniqueId"] == \
            user_name


# MARK: Cursors
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
    def __init__(self):
        super().__init__()
        self.cursor = int(time() * 1e3)

    def current_page(self):
        return self.cursor

    def next_page(self, data, query_parameters):
        old_cursor = self.cursor
        try:
            self.cursor = int(int(data["itemList"][-1]["createTime"]) * 1e3)
        except (IndexError, KeyError, ValueError):
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
    def __init__(self):
        super().__init__()
        self.cursor = 0

    def current_page(self):
        return self.cursor

    def next_page(self, data, query_parameters):
        self.cursor += int(data.get("TotalCount", query_parameters["count"]))
        return not data.get("hasMore", False)


# MARK: Requests
class TiktokPaginationRequest:
    def __init__(self, endpoint, cursor_type):
        self.endpoint = endpoint
        self.cursor_type = cursor_type
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
        cursor = self.cursor_type()
        for page in count(start=1):
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
                    final_page_reached = cursor.next_page(data,
                                                          final_parameters)
                    if self.exit_early(extractor, url) or final_page_reached:
                        return True
                    # Continue to next page and reset tries counter.
                    break
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

    # MARK: Interface

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

    # MARK: Helpers

    def _regenerate_device_id(self):
        self.device_id = str(randint(7250000000000000000, 7325099899999994577))

    def _request_data(self, extractor, cursor, query_parameters):
        url, final_parameters = self._build_api_request_url(cursor,
                                                            query_parameters)
        response = extractor.request(url)
        return (util.json_loads(response.text), final_parameters)

    def _build_api_request_url(self, cursor, extra_parameters):
        verify_fp = f"verify_{''.join(choices(hexdigits, k=7))}"
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
            # We must not write this as a floating-point number:
            "cursor": f"{floor(cursor.current_page())}",
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
            "verifyFp": verify_fp,
            "webcast_language": "en",
        }
        for key, value in extra_parameters.items():
            query_parameters[key] = f"{value}"
        query_str = "&".join([f"{name}={quote(value, safe='')}"
                              for name, value in query_parameters.items()])
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


# MARK: XYZ/item_list
class TiktokItemListRequest(TiktokPaginationRequest):
    def __init__(self, endpoint, cursor_type, type_of_items, range_predicate):
        super().__init__(endpoint, cursor_type)
        self.type_of_items = type_of_items
        self.range_predicate = range_predicate
        self.exit_early_due_to_no_items = False

    def extract_items(self, data):
        if "itemList" not in data:
            self.exit_early_due_to_no_items = True
            return {}
        return dict((item["id"], item) for item in data["itemList"])

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
        return [f"{profile_url}/video/{id}"
                for index, id in enumerate(reversed(sorted(self.items.keys())))
                if self._matches_filters(self.items.get(id), index + 1, video,
                                         photo, audio)]

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


# MARK: creator/item_list
class TiktokCreatorItemListRequest(TiktokItemListRequest):
    def __init__(self, range_predicate):
        super().__init__("creator/item_list", TiktokTimeCursor, "posts",
                         range_predicate)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "secUid" in query_parameters
        assert "type" in query_parameters
        # Pagination type: 0 == oldest-to-newest, 1 == newest-to-oldest.
        assert query_parameters["type"] == "0" or \
            query_parameters["type"] == "1"


# MARK: story/item_list
class TiktokStoryItemListRequest(TiktokItemListRequest):
    def __init__(self):
        super().__init__("story/item_list", TiktokItemCursor, "stories", None)

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        assert "authorId" in query_parameters
        assert "loadBackward" in query_parameters
        assert query_parameters["loadBackward"] == "false" or \
            query_parameters["loadBackward"] == "true"


# MARK: story/user_list
class TiktokStoryUserListRequest(TiktokPaginationRequest):
    def __init__(self):
        super().__init__("story/user_list", TiktokItemCursor)
        self.exit_early_due_to_no_cookies = False

    def validate_query_parameters(self, query_parameters):
        super().validate_query_parameters(query_parameters)
        # Not sure what this parameter does.
        assert "storyFeedScene" in query_parameters
        assert query_parameters["storyFeedScene"] == "3"

    def extract_items(self, data):
        if "storyUsers" not in data:
            self.exit_early_due_to_no_cookies = True
            return {}
        return dict((item["user"]["id"], item["user"]["uniqueId"])
                    for item in data["storyUsers"])

    def exit_early(self, extractor, url):
        if self.exit_early_due_to_no_cookies:
            extractor.log.error("You must provide cookies to extract the "
                                "stories of your following list")
        return self.exit_early_due_to_no_cookies

    def generate_urls(self):
        return [(name, f"https://www.tiktok.com/@{name}")
                for name in self.items.values()]
