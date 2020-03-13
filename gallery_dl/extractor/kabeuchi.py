# -*- coding: utf-8 -*-

# Copyright 2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://kabe-uchiroom.com/"""

from .common import Extractor, Message
from .. import text, exception


class KabeuchiUserExtractor(Extractor):
    """Extractor for all posts of a user on kabe-uchiroom.com"""
    category = "kabeuchi"
    subcategory = "user"
    directory_fmt = ("{category}", "{twitter_user_id} {twitter_id}")
    filename_fmt = "{id}_{num:>02}{title:?_//}.{extension}"
    archive_fmt = "{id}_{num}"
    root = "https://kabe-uchiroom.com"
    pattern = r"(?:https?://)?kabe-uchiroom\.com/mypage/?\?id=(\d+)"
    test = (
        ("https://kabe-uchiroom.com/mypage/?id=919865303848255493", {
            "pattern": (r"https://kabe-uchiroom\.com/accounts/upfile/3/"
                        r"919865303848255493/\w+\.jpe?g"),
            "count": ">= 24",
        }),
        ("https://kabe-uchiroom.com/mypage/?id=123456789", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = match.group(1)

    def items(self):
        base = "{}/accounts/upfile/{}/{}/".format(
            self.root, self.user_id[-1], self.user_id)
        keys = ("image1", "image2", "image3", "image4", "image5", "image6")

        for post in self.posts():
            if post.get("is_ad") or not post["image1"]:
                continue

            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%d %H:%M:%S")
            yield Message.Directory, post

            for key in keys:
                name = post[key]
                if not name:
                    break
                url = base + name
                post["num"] = ord(key[-1]) - 48
                yield Message.Url, url, text.nameext_from_url(name, post)

    def posts(self):
        url = "{}/mypage/?id={}".format(self.root, self.user_id)
        response = self.request(url)
        if response.history and response.url == self.root + "/":
            raise exception.NotFoundError("user")
        target_id = text.extract(response.text, 'user_friend_id = "', '"')[0]
        return self._pagination(target_id)

    def _pagination(self, target_id):
        url = "{}/get_posts.php".format(self.root)
        data = {
            "user_id"    : "0",
            "target_id"  : target_id,
            "type"       : "uploads",
            "sort_type"  : "0",
            "category_id": "all",
            "latest_post": "",
            "page_num"   : 0,
        }

        while True:
            info = self.request(url, method="POST", data=data).json()
            datas = info["datas"]

            if not datas or not isinstance(datas, list):
                return
            yield from datas

            last_id = datas[-1]["id"]
            if last_id == info["last_data"]:
                return
            data["latest_post"] = last_id
            data["page_num"] += 1
