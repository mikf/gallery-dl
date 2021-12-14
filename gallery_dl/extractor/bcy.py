# -*- coding: utf-8 -*-

# Copyright 2020-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bcy.net/"""

from .common import Extractor, Message
from .. import text, exception
import json
import re


class BcyExtractor(Extractor):
    """Base class for bcy extractors"""
    category = "bcy"
    directory_fmt = ("{category}", "{user[id]} {user[name]}")
    filename_fmt = "{post[id]} {id}.{extension}"
    archive_fmt = "{post[id]}_{id}"
    root = "https://bcy.net"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item_id = match.group(1)

    def items(self):
        sub = re.compile(r"^https?://p\d+-bcy\.byteimg\.com/img/banciyuan").sub
        iroot = "https://img-bcy-qn.pstatp.com"
        noop = self.config("noop")

        for post in self.posts():
            if not post["image_list"]:
                continue

            multi = None
            tags = post.get("post_tags") or ()
            data = {
                "user": {
                    "id"     : post["uid"],
                    "name"   : post["uname"],
                    "avatar" : sub(iroot, post["avatar"].partition("~")[0]),
                },
                "post": {
                    "id"     : text.parse_int(post["item_id"]),
                    "tags"   : [t["tag_name"] for t in tags],
                    "date"   : text.parse_timestamp(post["ctime"]),
                    "parody" : post["work"],
                    "content": post["plain"],
                    "likes"  : post["like_count"],
                    "shares" : post["share_count"],
                    "replies": post["reply_count"],
                },
            }

            yield Message.Directory, data
            for data["num"], image in enumerate(post["image_list"], 1):
                data["id"] = image["mid"]
                data["width"] = image["w"]
                data["height"] = image["h"]

                url = image["path"].partition("~")[0]
                text.nameext_from_url(url, data)

                if data["extension"]:
                    if not url.startswith(iroot):
                        url = sub(iroot, url)
                    data["filter"] = ""
                    yield Message.Url, url, data

                else:
                    if not multi:
                        if len(post["multi"]) < len(post["image_list"]):
                            multi = self._data_from_post(post["item_id"])
                            multi = multi["post_data"]["multi"]
                        else:
                            multi = post["multi"]
                    image = multi[data["num"] - 1]

                    if image["origin"]:
                        data["filter"] = "watermark"
                        yield Message.Url, image["origin"], data

                    if noop:
                        data["extension"] = ""
                        data["filter"] = "noop"
                        yield Message.Url, image["original_path"], data

    def posts(self):
        """Returns an iterable with all relevant 'post' objects"""

    def _data_from_post(self, post_id):
        url = "{}/item/detail/{}".format(self.root, post_id)
        page = self.request(url, notfound="post").text
        return json.loads(
            text.extract(page, 'JSON.parse("', '");')[0]
            .replace('\\\\u002F', '/')
            .replace('\\"', '"')
        )["detail"]


class BcyUserExtractor(BcyExtractor):
    """Extractor for user timelines"""
    subcategory = "user"
    pattern = r"(?:https?://)?bcy\.net/u/(\d+)"
    test = (
        ("https://bcy.net/u/1933712", {
            "pattern": r"https://img-bcy-qn.pstatp.com/\w+/\d+/post/\w+/.+jpg",
            "count": ">= 20",
        }),
        ("https://bcy.net/u/109282764041", {
            "pattern": r"https://p\d-bcy.byteimg.com/img/banciyuan/[0-9a-f]+"
                       r"~tplv-banciyuan-logo-v3:.+\.image",
            "range": "1-25",
            "count": 25,
        }),
    )

    def posts(self):
        url = self.root + "/apiv3/user/selfPosts"
        params = {"uid": self.item_id, "since": None}

        while True:
            data = self.request(url, params=params).json()

            try:
                items = data["data"]["items"]
            except KeyError:
                return
            if not items:
                return

            for item in items:
                yield item["item_detail"]
            params["since"] = item["since"]


class BcyPostExtractor(BcyExtractor):
    """Extractor for individual posts"""
    subcategory = "post"
    pattern = r"(?:https?://)?bcy\.net/item/detail/(\d+)"
    test = (
        ("https://bcy.net/item/detail/6355835481002893070", {
            "url": "301202375e61fd6e0e2e35de6c3ac9f74885dec3",
            "count": 1,
            "keyword": {
                "user": {
                    "id"     : 1933712,
                    "name"   : "wukloo",
                    "avatar" : "re:https://img-bcy-qn.pstatp.com/Public/",
                },
                "post": {
                    "id"     : 6355835481002893070,
                    "tags"   : list,
                    "date"   : "dt:2016-11-22 08:47:46",
                    "parody" : "东方PROJECT",
                    "content": "re:根据微博的建议稍微做了点修改",
                    "likes"  : int,
                    "shares" : int,
                    "replies": int,
                },
                "id": 8330182,
                "num": 1,
                "width" : 3000,
                "height": 1687,
                "filename": "712e0780b09011e696f973c3d1568337",
                "extension": "jpg",
            },
        }),
        # only watermarked images available
        ("https://bcy.net/item/detail/6950136331708144648", {
            "pattern": r"https://p\d-bcy.byteimg.com/img/banciyuan/[0-9a-f]+"
                       r"~tplv-banciyuan-logo-v3:.+\.image",
            "count": 8,
            "keyword": {"filter": "watermark"},
        }),
        # deleted
        ("https://bcy.net/item/detail/6780546160802143236", {
            "exception": exception.NotFoundError,
            "count": 0,
        }),
        # only visible to logged in users
        ("https://bcy.net/item/detail/6747523535150783495", {
            "count": 0,
        }),
    )

    def posts(self):
        try:
            data = self._data_from_post(self.item_id)
        except KeyError:
            return ()
        post = data["post_data"]
        post["image_list"] = post["multi"]
        post["plain"] = text.parse_unicode_escapes(post["plain"])
        post.update(data["detail_user"])
        return (post,)
