# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://chzzk.naver.com/"""

from .common import Extractor, Message
from .. import text, util


class NaverChzzkExtractor(Extractor):
    """Base class for chzzk.naver.com extractors"""
    category = "naver-chzzk"
    filename_fmt = "{uid}_{id}_{num}.{extension}"
    directory_fmt = ("{category}", "{user[userNickname]}")
    archive_fmt = "{uid}_{id}_{num}"

    def request_api(self, uid, id=None, params=None):
        return self.request_json(
            f"https://apis.naver.com/nng_main/nng_comment_api/v1/type"
            f"/CHANNEL_POST/id/{uid}/comments/{id or ''}",
            params=params)["content"]

    def items(self):
        for comment in self.comments():
            data = comment["comment"]
            files = data.pop("attaches") or ()
            data["id"] = data["commentId"]
            data["uid"] = data["objectId"]
            data["user"] = comment["user"]
            data["count"] = len(files)
            data["date"] = self.parse_datetime(
                data["createdDate"], "%Y%m%d%H%M%S")

            yield Message.Directory, "", data
            for data["num"], file in enumerate(files, 1):
                if extra := file.get("extraJson"):
                    file.update(util.json_loads(extra))
                file["date"] = self.parse_datetime_iso(
                    file["createdDate"])
                file["date_updated"] = self.parse_datetime_iso(
                    file["updatedDate"])
                data["file"] = file
                url = file["attachValue"]
                yield Message.Url, url, text.nameext_from_url(url, data)


class NaverChzzkCommentExtractor(NaverChzzkExtractor):
    """Extractor for individual comment from chzzk.naver.com"""
    subcategory = "comment"
    pattern = r"(?:https?://)?chzzk\.naver\.com/(\w+)/community/detail/(\d+)"
    example = "https://chzzk.naver.com/0123456789abcdef/community/detail/12345"

    def comments(self):
        uid, id = self.groups
        res = self.request_api(uid, id)
        return ({"comment": res["comment"], "user": res["user"]},)


class NaverChzzkCommunityExtractor(NaverChzzkExtractor):
    """Extractor for comments from chzzk.naver.com"""
    subcategory = "community"
    pattern = r"(?:https?://)?chzzk\.naver\.com/(\w+)/community"
    example = "https://chzzk.naver.com/0123456789abcdef/community"
    request_interval = (0.5, 1.5)

    def comments(self):
        uid = self.match[1]
        params = {
            "limit": 10,
            "offset": text.parse_int(self.config("offset")),
            "pagingType": "PAGE",
        }
        while True:
            comments = self.request_api(uid, params=params)["comments"]
            yield from comments["data"]
            if not comments["page"]["next"]:
                return
            params["offset"] += params["limit"]
