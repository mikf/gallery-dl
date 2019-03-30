# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.weibo.com/"""

from .common import Extractor, Message
from .. import text
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

    def items(self):
        first = True

        for status in self.statuses():

            obj = status
            num = 1

            if first:
                yield Message.Version, 1
                yield Message.Directory, status
                first = False

            while True:

                if "pics" in obj:
                    for image in obj["pics"]:
                        pid = image["pid"]
                        if "large" in image:
                            image = image["large"]
                        data = text.nameext_from_url(image["url"], {
                            "num": num,
                            "pid": pid,
                            "width": text.parse_int(image["geo"]["width"]),
                            "height": text.parse_int(image["geo"]["height"]),
                            "status": status,
                        })
                        yield Message.Url, image["url"], data
                        num += 1

                if "page_info" in obj and "media_info" in obj["page_info"]:
                    info = obj["page_info"]["media_info"]
                    url = info.get("stream_url_hd") or info["stream_url"]
                    data = text.nameext_from_url(url, {
                        "num": num,
                        "url": url,
                        "width": 0,
                        "height": 0,
                        "status": status,
                    })
                    yield Message.Url, url, data

                if self.retweets and "retweeted_status" in obj:
                    obj = obj["retweeted_status"]
                else:
                    break

    def statuses(self):
        """Returns an iterable containing all relevant 'status' objects"""


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

            for card in data["data"]["cards"]:
                if "mblog" in card:
                    yield card["mblog"]

            if len(data["data"]["cards"]) < 5:
                return
            params["page"] += 1


class WeiboStatusExtractor(WeiboExtractor):
    """Extractor for images from a status on weibo.cn"""
    subcategory = "status"
    pattern = (r"(?:https?://)?(?:www\.|m\.)?weibo\.c(?:om|n)"
               r"/(?:detail|status|\d+)/(\d+)")
    test = (
        ("https://m.weibo.cn/detail/4323047042991618", {
            "pattern": r"https?://wx\d+.sinaimg.cn/large/\w+.jpg",
        }),
        ("https://m.weibo.cn/detail/4339748116375525", {
            "pattern": r"https?://f.us.sinaimg.cn/\w+\.mp4\?label=mp4_hd",
        }),
        ("https://m.weibo.cn/status/4339748116375525"),
        ("https://m.weibo.cn/5746766133/4339748116375525"),
    )

    def __init__(self, match):
        WeiboExtractor.__init__(self, match)
        self.status_id = match.group(1)

    def statuses(self):
        url = "{}/detail/{}".format(self.root, self.status_id)
        page = self.request(url).text
        data = json.loads(text.extract(
            page, " var $render_data = [", "][0] || {};")[0])
        return (data["status"],)
