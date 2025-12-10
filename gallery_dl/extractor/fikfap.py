# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://fikfap.com/"""

from .common import Extractor, Message
from .. import text, exception

BASE_PATTERN = r"(?:https?://)?(?:www\.)?fikfap\.com"


class FikfapExtractor(Extractor):
    """Base class for fikfap extractors"""
    category = "fikfap"
    root = "https://fikfap.com"
    root_api = "https://api.fikfap.com"
    directory_fmt = ("{category}", "{author[username]}")
    filename_fmt = "{postId} {label[:240]}.{extension}"
    archive_fmt = "{postId}"

    def items(self):
        headers = {
            "Referer"       : self.root + "/",
            "Origin"        : self.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

        for post in self.posts():
            if url := post.get("videoFileOriginalUrl"):
                post["extension"] = text.ext_from_url(url)
            elif url := post.get("videoStreamUrl"):
                url = "ytdl:" + url
                post["extension"] = "mp4"
                post["_ytdl_manifest"] = "hls"
                post["_ytdl_manifest_headers"] = headers
            else:
                self.log.warning("%s: No video available", post["postId"])
                continue

            post["date"] = self.parse_datetime_iso(post["createdAt"])
            post["date_updated"] = self.parse_datetime_iso(post["updatedAt"])
            post["tags"] = [t["label"] for t in post["hashtags"]]
            post["filename"] = post["label"]

            yield Message.Directory, "", post
            yield Message.Url, url, post

    def request_api(self, url, params):
        return self.request_json(url, params=params, headers={
            "Referer"       : self.root + "/",
            "Authorization-Anonymous": "2527cc30-c3c5-41be-b8bb-104b6ea7a206",
            "IsLoggedIn"    : "false",
            "IsPWA"         : "false",
            "Origin"        : self.root,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        })


class FikfapPostExtractor(FikfapExtractor):
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/user/(\w+)/post/(\d+)"
    example = "https://fikfap.com/user/USER/post/12345"

    def posts(self):
        user, pid = self.groups

        url = f"{self.root_api}/profile/username/{user}/posts"
        params = {"amount" : "1", "startId": pid}
        posts = self.request_api(url, params)

        pid = int(pid)
        for post in posts:
            if post["postId"] == pid:
                return (post,)
        raise exception.NotFoundError("post")


class FikfapUserExtractor(FikfapExtractor):
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}/user/(\w+)"
    example = "https://fikfap.com/user/USER"

    def posts(self):
        user = self.groups[0]

        url = f"{self.root_api}/profile/username/{user}/posts"
        params = {"amount": "21"}

        while True:
            data = self.request_api(url, params)

            yield from data

            if len(data) < 21:
                return
            params["afterId"] = data[-1]["postId"]
