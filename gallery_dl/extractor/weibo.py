# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weibo.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
import itertools
import random
import json


class WeiboExtractor(Extractor):
    category = "weibo"
    directory_fmt = ("{category}", "{user[screen_name]}")
    filename_fmt = "{status[id]}_{num:>02}.{extension}"
    archive_fmt = "{status[id]}_{num}"
    root = "https://weibo.com"
    request_interval = (1.0, 2.0)

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.retweets = self.config("retweets", True)
        self.videos = self.config("videos", True)
        self.livephoto = self.config("livephoto", True)

        cookies = _cookie_cache()
        if cookies is not None:
            self.session.cookies.update(cookies)

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)

        if not response.history or "passport.weibo.com" not in response.url:
            return response

        self.log.info("Sina Visitor System")

        passport_url = "https://passport.weibo.com/visitor/genvisitor"
        headers = {"Referer": response.url}
        data = {
            "cb": "gen_callback",
            "fp": '{"os":"1","browser":"Gecko91,0,0,0","fonts":"undefined",'
                  '"screenInfo":"1920*1080*24","plugins":""}',
        }

        page = Extractor.request(
            self, passport_url, method="POST", headers=headers, data=data).text
        data = json.loads(text.extract(page, "(", ");")[0])["data"]

        passport_url = "https://passport.weibo.com/visitor/visitor"
        params = {
            "a"    : "incarnate",
            "t"    : data["tid"],
            "w"    : "2",
            "c"    : "{:>03}".format(data["confidence"]),
            "gc"   : "",
            "cb"   : "cross_domain",
            "from" : "weibo",
            "_rand": random.random(),
        }
        response = Extractor.request(self, passport_url, params=params)

        _cookie_cache.update("", response.cookies)

        return Extractor.request(self, url, **kwargs)

    def items(self):
        original_retweets = (self.retweets == "original")

        for status in self.statuses():

            status["date"] = text.parse_datetime(
                status["created_at"], "%a %b %d %H:%M:%S %z %Y")
            yield Message.Directory, status

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
                if "filename" not in file:
                    text.nameext_from_url(file["url"], file)
                file["status"] = status
                file["num"] = num
                yield Message.Url, file["url"], file

    def _status_by_id(self, status_id):
        url = "{}/ajax/statuses/show?id={}".format(self.root, status_id)
        return self.request(url).json()

    def _files_from_status(self, status):
        pic_ids = status.get("pic_ids")
        if pic_ids:
            pics = status["pic_infos"]
            for pic_id in pic_ids:
                pic = pics[pic_id]
                yield pic["largest"].copy()

                if pic.get("type") == "livephoto" and self.livephoto:
                    file = {"url": pic["video"]}
                    file["filehame"], _, file["extension"] = \
                        pic["video"].rpartition("%2F")[2].rpartition(".")
                    yield file

        if "page_info" in status:
            page_info = status["page_info"]
            if "media_info" not in page_info or not self.videos:
                return
            media = max(page_info["media_info"]["playback_list"],
                        key=lambda m: m["meta"]["quality_index"])
            yield media["play_info"].copy()


class WeiboUserExtractor(WeiboExtractor):
    """Extractor for all images of a user on weibo.cn"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
               r"/(?:u|p(?:rofile)?)/(\d+)")
    test = (
        ("https://m.weibo.cn/u/2314621010", {
            "range": "1-30",
        }),
        # deleted (#2521)
        ("https://weibo.com/u/7500315942", {
            "count": 0,
        }),
        ("https://m.weibo.cn/profile/2314621010"),
        ("https://m.weibo.cn/p/2304132314621010_-_WEIBO_SECOND_PROFILE_WEIBO"),
        ("https://www.weibo.com/p/1003062314621010/home"),
    )

    def __init__(self, match):
        WeiboExtractor.__init__(self, match)
        self.user_id = match.group(1)[-10:]

    def statuses(self):
        url = self.root + "/ajax/statuses/mymblog"
        params = {
            "uid": self.user_id,
            "feature": "0",
        }
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "X-XSRF-TOKEN": None,
            "Referer": "{}/u/{}".format(self.root, self.user_id),
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

            statuses = data["data"]["list"]
            if not statuses:
                return
            yield from statuses

            params["since_id"] = statuses[-1]["id"] - 1


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
            "pattern": r"https?://f.us.sinaimg.cn/\w+\.mp4\?label=mp4_1080p",
        }),
        # unavailable video (#427)
        ("https://m.weibo.cn/status/4268682979207023", {
            "exception": exception.HttpError,
        }),
        # non-numeric status ID (#664)
        ("https://weibo.com/3314883543/Iy7fj4qVg"),
        # original retweets (#1542)
        ("https://m.weibo.cn/detail/4600272267522211", {
            "options": (("retweets", "original"),),
            "keyword": {"status": {"id": 4600167083287033}},
        }),
        # livephoto (#2146)
        ("https://weibo.com/5643044717/KkuDZ4jAA", {
            "range": "2,4,6",
            "pattern": r"https://video\.weibo\.com/media/play\?livephoto="
                       r"https%3A%2F%2Fus.sinaimg.cn%2F\w+\.mov",
        }),
        ("https://m.weibo.cn/status/4339748116375525"),
        ("https://m.weibo.cn/5746766133/4339748116375525"),
    )

    def __init__(self, match):
        WeiboExtractor.__init__(self, match)
        self.status_id = match.group(1)

    def statuses(self):
        return (self._status_by_id(self.status_id),)


@cache(maxage=356*86400)
def _cookie_cache():
    return None
