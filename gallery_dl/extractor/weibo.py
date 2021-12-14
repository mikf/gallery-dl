# -*- coding: utf-8 -*-

# Copyright 2019-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weibo.com/"""

from .common import Extractor, Message
from .. import text, exception
import itertools
import json


class WeiboExtractor(Extractor):
    category = "weibo"
    directory_fmt = ("{category}", "{user[screen_name]}")
    filename_fmt = "{status[id]}_{num:>02}.{extension}"
    archive_fmt = "{status[id]}_{num}"
    root = "https://m.weibo.cn"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.retweets = self.config("retweets", True)
        self.videos = self.config("videos", True)

    def items(self):
        original_retweets = (self.retweets == "original")

        for status in self.statuses():

            if self.retweets and "retweeted_status" in status:
                if original_retweets:
                    status = status["retweeted_status"]
                    files = self._files_from_status(status)
                else:
                    files = itertools.chain(
                        self._files_from_status(status),
                        self._files_from_status(status["retweeted_status"]),
                    )
            else:
                files = self._files_from_status(status)

            for num, file in enumerate(files, 1):
                if num == 1:
                    status["date"] = text.parse_datetime(
                        status["created_at"], "%a %b %d %H:%M:%S %z %Y")
                    yield Message.Directory, status
                file["status"] = status
                file["num"] = num
                yield Message.Url, file["url"], file

    def statuses(self):
        """Returns an iterable containing all relevant 'status' objects"""

    def _status_by_id(self, status_id):
        url = "{}/detail/{}".format(self.root, status_id)
        page = self.request(url, fatal=False).text
        data = text.extract(page, "var $render_data = [", "][0] || {};")[0]
        return json.loads(data)["status"] if data else None

    def _files_from_status(self, status):
        page_info = status.pop("page_info", ())
        if "pics" in status:
            if len(status["pics"]) < status["pic_num"]:
                status = self._status_by_id(status["id"]) or status
            for image in status.pop("pics"):
                pid = image["pid"]
                if "large" in image:
                    image = image["large"]
                geo = image.get("geo") or {}
                yield text.nameext_from_url(image["url"], {
                    "url"   : image["url"],
                    "pid"   : pid,
                    "width" : text.parse_int(geo.get("width")),
                    "height": text.parse_int(geo.get("height")),
                })

        if self.videos and "media_info" in page_info:
            info = page_info["media_info"]
            url = info.get("stream_url_hd") or info.get("stream_url")
            if url:
                data = text.nameext_from_url(url, {
                    "url"   : url,
                    "pid"   : 0,
                    "width" : 0,
                    "height": 0,
                })
                if data["extension"] == "m3u8":
                    data["extension"] = "mp4"
                    data["url"] = "ytdl:" + url
                    data["_ytdl_extra"] = {"protocol": "m3u8_native"}
                yield data


class WeiboUserExtractor(WeiboExtractor):
    """Extractor for all images of a user on weibo.cn"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
               r"/(?:u|p(?:rofile)?)/(\d+)")
    test = (
        ("https://m.weibo.cn/u/2314621010", {
            "range": "1-30",
        }),
        ("https://m.weibo.cn/profile/2314621010"),
        ("https://m.weibo.cn/p/2304132314621010_-_WEIBO_SECOND_PROFILE_WEIBO"),
        ("https://www.weibo.com/p/1003062314621010/home"),
    )

    def __init__(self, match):
        WeiboExtractor.__init__(self, match)
        self.user_id = match.group(1)

    def statuses(self):
        url = self.root + "/api/container/getIndex"
        params = {"page": 1, "containerid": "107603" + self.user_id[-10:]}

        while True:
            data = self.request(url, params=params).json()
            cards = data["data"]["cards"]

            if not cards:
                return
            for card in cards:
                if "mblog" in card:
                    yield card["mblog"]
            params["page"] += 1


class WeiboStatusExtractor(WeiboExtractor):
    """Extractor for images from a status on weibo.cn"""
    subcategory = "status"
    pattern = (r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
               r"/(?:detail|status|\d+)/(\w+)")
    test = (
        ("https://m.weibo.cn/detail/4323047042991618", {
            "pattern": r"https?://wx\d+.sinaimg.cn/large/\w+.jpg",
            "keyword": {"status": {"date": "dt:2018-12-30 13:56:36"}},
        }),
        ("https://m.weibo.cn/detail/4339748116375525", {
            "pattern": r"https?://f.us.sinaimg.cn/\w+\.mp4\?label=mp4_hd",
        }),
        # unavailable video (#427)
        ("https://m.weibo.cn/status/4268682979207023", {
            "exception": exception.NotFoundError,
        }),
        # non-numeric status ID (#664)
        ("https://weibo.com/3314883543/Iy7fj4qVg"),
        # original retweets (#1542)
        ("https://m.weibo.cn/detail/4600272267522211", {
            "options": (("retweets", "original"),),
            "keyword": {"status": {"id": "4600167083287033"}},
        }),
        ("https://m.weibo.cn/status/4339748116375525"),
        ("https://m.weibo.cn/5746766133/4339748116375525"),
    )

    def __init__(self, match):
        WeiboExtractor.__init__(self, match)
        self.status_id = match.group(1)

    def statuses(self):
        status = self._status_by_id(self.status_id)
        if not status:
            raise exception.NotFoundError("status")
        return (status,)
