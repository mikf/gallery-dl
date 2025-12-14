# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weibo.com/"""

from .common import Extractor, Message, Dispatch
from .. import text, util, exception
from ..cache import cache
import random

BASE_PATTERN = r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
USER_PATTERN = rf"{BASE_PATTERN}/(?:(u|n|p(?:rofile)?)/)?([^/?#]+)(?:/home)?"


class WeiboExtractor(Extractor):
    category = "weibo"
    directory_fmt = ("{category}", "{user[screen_name]}")
    filename_fmt = "{status[id]}_{num:>02}.{extension}"
    archive_fmt = "{status[id]}_{num}"
    cookies_domain = ".weibo.com"
    cookies_names = ("SUB", "SUBP")
    root = "https://weibo.com"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self._prefix, self.user = match.groups()

    def _init(self):
        self.livephoto = self.config("livephoto", True)
        self.retweets = self.config("retweets", False)
        self.longtext = self.config("text", False)
        self.videos = self.config("videos", True)
        self.movies = self.config("movies", False)
        self.gifs = self.config("gifs", True)
        self.gifs_video = (self.gifs == "video")

        cookies = _cookie_cache()
        if cookies is None:
            self.logged_in = self.cookies_check(
                self.cookies_names, self.cookies_domain)
            return

        domain = self.cookies_domain
        cookies = {c.name: c for c in cookies if c.domain == domain}
        for cookie in self.cookies:
            if cookie.domain == domain and cookie.name in cookies:
                del cookies[cookie.name]
                if not cookies:
                    self.logged_in = True
                    return

        self.logged_in = False
        for cookie in cookies.values():
            self.cookies.set_cookie(cookie)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history:
            if "login.sina.com" in response.url:
                raise exception.AbortExtraction(
                    f"HTTP redirect to login page "
                    f"({response.url.partition('?')[0]})")
            if "passport.weibo.com" in response.url:
                self._sina_visitor_system(response)
                response = Extractor.request(self, url, **kwargs)

        return response

    def items(self):
        original_retweets = (self.retweets == "original")

        for status in self.statuses():

            if "ori_mid" in status and not self.retweets:
                self.log.debug("Skipping %s (快转 retweet)", status["id"])
                continue

            if "retweeted_status" in status:
                if not self.retweets:
                    self.log.debug("Skipping %s (retweet)", status["id"])
                    continue

                # videos of the original post are in status
                # images of the original post are in status["retweeted_status"]
                files = []
                self._extract_status(status, files)
                self._extract_status(status["retweeted_status"], files)

                if original_retweets:
                    status = status["retweeted_status"]
            else:
                files = []
                self._extract_status(status, files)

            if self.longtext and status.get("isLongText") and \
                    status["text"].endswith('class="expand">展开</span>'):
                status = self._status_by_id(status["id"])

            status["date"] = self.parse_datetime(
                status["created_at"], "%a %b %d %H:%M:%S %z %Y")
            status["count"] = len(files)
            yield Message.Directory, "", status

            num = 0
            for file in files:
                url = file["url"]
                if not url:
                    continue
                if url.startswith("http:"):
                    url = f"https:{url[5:]}"
                if "filename" not in file:
                    text.nameext_from_url(url, file)
                    if file["extension"] == "json":
                        file["extension"] = "mp4"
                if file["extension"] == "m3u8":
                    url = f"ytdl:{url}"
                    file["_ytdl_manifest"] = "hls"
                    file["extension"] = "mp4"
                num += 1
                file["status"] = status
                file["num"] = num
                yield Message.Url, url, file

    def _extract_status(self, status, files):
        if "mix_media_info" in status:
            for item in status["mix_media_info"]["items"]:
                type = item.get("type")
                if type == "video":
                    if self.videos:
                        files.append(self._extract_video(
                            item["data"]["media_info"]))
                elif type == "pic":
                    files.append(item["data"]["largest"].copy())
                else:
                    self.log.warning("Unknown media type '%s'", type)
            return

        if pic_ids := status.get("pic_ids"):
            pics = status["pic_infos"]
            for pic_id in pic_ids:
                pic = pics[pic_id]
                pic_type = pic.get("type")

                if pic_type == "gif" and self.gifs:
                    if self.gifs_video:
                        files.append({"url": pic["video"]})
                    else:
                        files.append(pic["largest"].copy())

                elif pic_type == "livephoto" and self.livephoto:
                    files.append(pic["largest"].copy())
                    files.append({"url": pic["video"]})

                else:
                    files.append(pic["largest"].copy())

        if "page_info" in status:
            info = status["page_info"]
            if "media_info" in info and self.videos:
                if info.get("type") != "5" or self.movies:
                    files.append(self._extract_video(info["media_info"]))
                else:
                    self.log.debug("%s: Ignoring 'movie' video", status["id"])

    def _extract_video(self, info):
        if info.get("live_status") == 1:
            self.log.debug("Skipping ongoing live stream")
            return {"url": ""}

        try:
            media = max(info["playback_list"],
                        key=lambda m: m["meta"]["quality_index"])
        except Exception:
            video = {"url": (info.get("replay_hd") or
                             info.get("stream_url_hd") or
                             info.get("stream_url") or "")}
        else:
            video = media["play_info"].copy()

        if "//wblive-out." in video["url"] and \
                not text.ext_from_url(video["url"]):
            try:
                video["url"] = self.request_location(video["url"])
            except exception.HttpError as exc:
                self.log.warning("%s: %s", exc.__class__.__name__, exc)
                video["url"] = ""

        return video

    def _status_by_id(self, status_id):
        url = (f"{self.root}/ajax/statuses/show"
               f"?id={status_id}&isGetLongText=true")
        return self.request_json(url)

    def _user_id(self):
        if len(self.user) >= 10 and self.user.isdecimal():
            return self.user[-10:]
        else:
            url = (f"{self.root}/ajax/profile/info?"
                   f"{'screen_name' if self._prefix == 'n' else 'custom'}="
                   f"{self.user}")
            return self.request_json(url)["data"]["user"]["idstr"]

    def _pagination(self, endpoint, params):
        url = f"{self.root}/ajax{endpoint}"
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": None,
            "Referer": f"{self.root}/u/{params['uid']}",
        }

        while True:
            response = self.request(url, params=params, headers=headers)
            headers["Accept"] = "application/json, text/plain, */*"
            headers["X-XSRF-TOKEN"] = response.cookies.get("XSRF-TOKEN")

            data = response.json()
            if not data.get("ok"):
                self.log.debug(response.content)
                if "since_id" not in params:  # first iteration
                    raise exception.AbortExtraction(
                        f'"{data.get("msg") or "unknown error"}"')

            try:
                data = data["data"]
                statuses = data["list"]
            except KeyError:
                return

            yield from statuses

            # videos, newvideo
            if cursor := data.get("next_cursor"):
                if cursor == -1:
                    return
                params["cursor"] = cursor
                continue

            # album
            if since_id := data.get("since_id"):
                params["sinceid"] = since_id
                if "page" in params:
                    params["page"] += 1
                continue

            # home, article
            if "page" in params:
                if not statuses:
                    return
                params["page"] += 1
                continue

            # feed, last album page
            try:
                params["since_id"] = statuses[-1]["id"] - 1
            except LookupError:
                return

    def _sina_visitor_system(self, response):
        self.log.info("Sina Visitor System")

        passport_url = "https://passport.weibo.com/visitor/genvisitor"
        headers = {"Referer": response.url}
        data = {
            "cb": "gen_callback",
            "fp": '{"os":"1","browser":"Gecko109,0,0,0","fonts":"undefined",'
                  '"screenInfo":"1920*1080*24","plugins":""}',
        }

        page = Extractor.request(
            self, passport_url, method="POST", headers=headers, data=data).text
        data = util.json_loads(text.extr(page, "(", ");"))["data"]

        passport_url = "https://passport.weibo.com/visitor/visitor"
        params = {
            "a"    : "incarnate",
            "t"    : data["tid"],
            "w"    : "3" if data.get("new_tid") else "2",
            "c"    : f"{data.get('confidence') or 100:>03}",
            "gc"   : "",
            "cb"   : "cross_domain",
            "from" : "weibo",
            "_rand": random.random(),
        }
        response = Extractor.request(self, passport_url, params=params)
        _cookie_cache.update("", response.cookies)


class WeiboUserExtractor(WeiboExtractor):
    """Extractor for weibo user profiles"""
    subcategory = "user"
    pattern = rf"{USER_PATTERN}(?:$|#)"
    example = "https://weibo.com/USER"

    # do NOT override 'initialize()'
    # it is needed for 'self._user_id()'
    # def initialize(self):
    #     pass

    def items(self):
        base = f"{self.root}/u/{self._user_id()}?tabtype="
        return Dispatch._dispatch_extractors(self, (
            (WeiboHomeExtractor    , f"{base}home"),
            (WeiboFeedExtractor    , f"{base}feed"),
            (WeiboVideosExtractor  , f"{base}video"),
            (WeiboNewvideoExtractor, f"{base}newVideo"),
            (WeiboAlbumExtractor   , f"{base}album"),
        ), ("feed",))


class WeiboHomeExtractor(WeiboExtractor):
    """Extractor for weibo 'home' listings"""
    subcategory = "home"
    pattern = rf"{USER_PATTERN}\?tabtype=home"
    example = "https://weibo.com/USER?tabtype=home"

    def statuses(self):
        endpoint = "/profile/myhot"
        params = {"uid": self._user_id(), "page": 1, "feature": "2"}
        return self._pagination(endpoint, params)


class WeiboFeedExtractor(WeiboExtractor):
    """Extractor for weibo user feeds"""
    subcategory = "feed"
    pattern = rf"{USER_PATTERN}\?tabtype=feed"
    example = "https://weibo.com/USER?tabtype=feed"

    def statuses(self):
        endpoint = "/statuses/mymblog"
        params = {"uid": self._user_id(), "feature": "0"}
        if self.logged_in:
            params["page"] = 1
        return self._pagination(endpoint, params)


class WeiboVideosExtractor(WeiboExtractor):
    """Extractor for weibo 'video' listings"""
    subcategory = "videos"
    pattern = rf"{USER_PATTERN}\?tabtype=video"
    example = "https://weibo.com/USER?tabtype=video"

    def statuses(self):
        endpoint = "/profile/getprofilevideolist"
        params = {"uid": self._user_id()}

        for status in self._pagination(endpoint, params):
            yield status["video_detail_vo"]


class WeiboNewvideoExtractor(WeiboExtractor):
    """Extractor for weibo 'newVideo' listings"""
    subcategory = "newvideo"
    pattern = rf"{USER_PATTERN}\?tabtype=newVideo"
    example = "https://weibo.com/USER?tabtype=newVideo"

    def statuses(self):
        endpoint = "/profile/getWaterFallContent"
        params = {"uid": self._user_id()}
        return self._pagination(endpoint, params)


class WeiboArticleExtractor(WeiboExtractor):
    """Extractor for weibo 'article' listings"""
    subcategory = "article"
    pattern = rf"{USER_PATTERN}\?tabtype=article"
    example = "https://weibo.com/USER?tabtype=article"

    def statuses(self):
        endpoint = "/statuses/mymblog"
        params = {"uid": self._user_id(), "page": 1, "feature": "10"}
        return self._pagination(endpoint, params)


class WeiboAlbumExtractor(WeiboExtractor):
    """Extractor for weibo 'album' listings"""
    subcategory = "album"
    pattern = rf"{USER_PATTERN}\?tabtype=album"
    example = "https://weibo.com/USER?tabtype=album"

    def statuses(self):
        endpoint = "/profile/getImageWall"
        params = {"uid": self._user_id()}

        seen = set()
        for image in self._pagination(endpoint, params):
            mid = image["mid"]
            if mid not in seen:
                seen.add(mid)
                status = self._status_by_id(mid)
                if status.get("ok") != 1:
                    self.log.debug("Skipping status %s (%s)", mid, status)
                else:
                    yield status


class WeiboStatusExtractor(WeiboExtractor):
    """Extractor for a weibo status"""
    subcategory = "status"
    pattern = rf"{BASE_PATTERN}/(detail|status|\d+)/(\w+)"
    example = "https://weibo.com/detail/12345"

    def statuses(self):
        status = self._status_by_id(self.user)
        if status.get("ok") != 1:
            self.log.debug(status)
            raise exception.NotFoundError("status")
        return (status,)


@cache(maxage=365*86400)
def _cookie_cache():
    return None
