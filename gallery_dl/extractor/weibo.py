# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weibo.com/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache
import random

BASE_PATTERN = r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
USER_PATTERN = BASE_PATTERN + r"/(?:(u|n|p(?:rofile)?)/)?([^/?#]+)(?:/home)?"


class WeiboExtractor(Extractor):
    category = "weibo"
    directory_fmt = ("{category}", "{user[screen_name]}")
    filename_fmt = "{status[id]}_{num:>02}.{extension}"
    archive_fmt = "{status[id]}_{num}"
    root = "https://weibo.com"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self._prefix, self.user = match.groups()

    def _init(self):
        self.livephoto = self.config("livephoto", True)
        self.retweets = self.config("retweets", False)
        self.videos = self.config("videos", True)
        self.movies = self.config("movies", False)
        self.gifs = self.config("gifs", True)
        self.gifs_video = (self.gifs == "video")

        cookies = _cookie_cache()
        if cookies is not None:
            self.cookies.update(cookies)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if response.history:
            if "login.sina.com" in response.url:
                raise exception.StopExtraction(
                    "HTTP redirect to login page (%s)",
                    response.url.partition("?")[0])
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

            status["date"] = text.parse_datetime(
                status["created_at"], "%a %b %d %H:%M:%S %z %Y")
            status["count"] = len(files)
            yield Message.Directory, status

            for num, file in enumerate(files, 1):
                if file["url"].startswith("http:"):
                    file["url"] = "https:" + file["url"][5:]
                if "filename" not in file:
                    text.nameext_from_url(file["url"], file)
                    if file["extension"] == "json":
                        file["extension"] = "mp4"
                file["status"] = status
                file["num"] = num
                yield Message.Url, file["url"], file

    def _extract_status(self, status, files):
        append = files.append

        if "mix_media_info" in status:
            for item in status["mix_media_info"]["items"]:
                type = item.get("type")
                if type == "video":
                    if self.videos:
                        append(self._extract_video(item["data"]["media_info"]))
                elif type == "pic":
                    append(item["data"]["largest"].copy())
                else:
                    self.log.warning("Unknown media type '%s'", type)
            return

        pic_ids = status.get("pic_ids")
        if pic_ids:
            pics = status["pic_infos"]
            for pic_id in pic_ids:
                pic = pics[pic_id]
                pic_type = pic.get("type")

                if pic_type == "gif" and self.gifs:
                    if self.gifs_video:
                        append({"url": pic["video"]})
                    else:
                        append(pic["largest"].copy())

                elif pic_type == "livephoto" and self.livephoto:
                    append(pic["largest"].copy())
                    append({"url": pic["video"]})

                else:
                    append(pic["largest"].copy())

        if "page_info" in status:
            info = status["page_info"]
            if "media_info" in info and self.videos:
                if info.get("type") != "5" or self.movies:
                    append(self._extract_video(info["media_info"]))
                else:
                    self.log.debug("%s: Ignoring 'movie' video", status["id"])

    def _extract_video(self, info):
        try:
            media = max(info["playback_list"],
                        key=lambda m: m["meta"]["quality_index"])
        except Exception:
            return {"url": (info.get("stream_url_hd") or
                            info.get("stream_url") or "")}
        else:
            return media["play_info"].copy()

    def _status_by_id(self, status_id):
        url = "{}/ajax/statuses/show?id={}".format(self.root, status_id)
        return self.request(url).json()

    def _user_id(self):
        if len(self.user) >= 10 and self.user.isdecimal():
            return self.user[-10:]
        else:
            url = "{}/ajax/profile/info?{}={}".format(
                self.root,
                "screen_name" if self._prefix == "n" else "custom",
                self.user)
            return self.request(url).json()["data"]["user"]["idstr"]

    def _pagination(self, endpoint, params):
        url = self.root + "/ajax" + endpoint
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": None,
            "Referer": "{}/u/{}".format(self.root, params["uid"]),
        }

        while True:
            response = self.request(url, params=params, headers=headers)
            headers["Accept"] = "application/json, text/plain, */*"
            headers["X-XSRF-TOKEN"] = response.cookies.get("XSRF-TOKEN")

            data = response.json()
            if not data.get("ok"):
                self.log.debug(response.content)
                if "since_id" not in params:  # first iteration
                    raise exception.StopExtraction(
                        '"%s"', data.get("msg") or "unknown error")

            data = data["data"]
            statuses = data["list"]
            yield from statuses

            # videos, newvideo
            cursor = data.get("next_cursor")
            if cursor:
                if cursor == -1:
                    return
                params["cursor"] = cursor
                continue

            # album
            since_id = data.get("since_id")
            if since_id:
                params["sinceid"] = data["since_id"]
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
            "c"    : "{:>03}".format(data.get("confidence") or 100),
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
    pattern = USER_PATTERN + r"(?:$|#)"
    example = "https://weibo.com/USER"

    # do NOT override 'initialize()'
    # it is needed for 'self._user_id()'
    # def initialize(self):
    #     pass

    def items(self):
        base = "{}/u/{}?tabtype=".format(self.root, self._user_id())
        return self._dispatch_extractors((
            (WeiboHomeExtractor    , base + "home"),
            (WeiboFeedExtractor    , base + "feed"),
            (WeiboVideosExtractor  , base + "video"),
            (WeiboNewvideoExtractor, base + "newVideo"),
            (WeiboAlbumExtractor   , base + "album"),
        ), ("feed",))


class WeiboHomeExtractor(WeiboExtractor):
    """Extractor for weibo 'home' listings"""
    subcategory = "home"
    pattern = USER_PATTERN + r"\?tabtype=home"
    example = "https://weibo.com/USER?tabtype=home"

    def statuses(self):
        endpoint = "/profile/myhot"
        params = {"uid": self._user_id(), "page": 1, "feature": "2"}
        return self._pagination(endpoint, params)


class WeiboFeedExtractor(WeiboExtractor):
    """Extractor for weibo user feeds"""
    subcategory = "feed"
    pattern = USER_PATTERN + r"\?tabtype=feed"
    example = "https://weibo.com/USER?tabtype=feed"

    def statuses(self):
        endpoint = "/statuses/mymblog"
        params = {"uid": self._user_id(), "feature": "0"}
        return self._pagination(endpoint, params)


class WeiboVideosExtractor(WeiboExtractor):
    """Extractor for weibo 'video' listings"""
    subcategory = "videos"
    pattern = USER_PATTERN + r"\?tabtype=video"
    example = "https://weibo.com/USER?tabtype=video"

    def statuses(self):
        endpoint = "/profile/getprofilevideolist"
        params = {"uid": self._user_id()}

        for status in self._pagination(endpoint, params):
            yield status["video_detail_vo"]


class WeiboNewvideoExtractor(WeiboExtractor):
    """Extractor for weibo 'newVideo' listings"""
    subcategory = "newvideo"
    pattern = USER_PATTERN + r"\?tabtype=newVideo"
    example = "https://weibo.com/USER?tabtype=newVideo"

    def statuses(self):
        endpoint = "/profile/getWaterFallContent"
        params = {"uid": self._user_id()}
        return self._pagination(endpoint, params)


class WeiboArticleExtractor(WeiboExtractor):
    """Extractor for weibo 'article' listings"""
    subcategory = "article"
    pattern = USER_PATTERN + r"\?tabtype=article"
    example = "https://weibo.com/USER?tabtype=article"

    def statuses(self):
        endpoint = "/statuses/mymblog"
        params = {"uid": self._user_id(), "page": 1, "feature": "10"}
        return self._pagination(endpoint, params)


class WeiboAlbumExtractor(WeiboExtractor):
    """Extractor for weibo 'album' listings"""
    subcategory = "album"
    pattern = USER_PATTERN + r"\?tabtype=album"
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
    """Extractor for images from a status on weibo.cn"""
    subcategory = "status"
    pattern = BASE_PATTERN + r"/(detail|status|\d+)/(\w+)"
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
