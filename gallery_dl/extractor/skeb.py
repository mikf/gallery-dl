# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://skeb.jp/"""

from .common import Extractor, Message
from .. import text
import itertools


class SkebExtractor(Extractor):
    """Base class for skeb extractors"""
    category = "skeb"
    directory_fmt = ("{category}", "{creator[screen_name]}")
    filename_fmt = "{post_num}_{file_id}.{extension}"
    archive_fmt = "{post_num}_{file_id}_{content_category}"
    root = "https://skeb.jp"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_name = match.group(1)
        self.thumbnails = self.config("thumbnails", False)

    def items(self):
        for user_name, post_num in self.posts():
            response, post = self._get_post_data(user_name, post_num)
            yield Message.Directory, post
            for data in self._get_urls_from_post(response, post):
                url = data["file_url"]
                yield Message.Url, url, text.nameext_from_url(url, data)

    def posts(self):
        """Return post number"""

    def _pagination(self, url, params):
        headers = {"Referer": self.root, "Authorization": "Bearer null"}
        params["offset"] = 0

        while True:
            posts = self.request(url, params=params, headers=headers).json()

            for post in posts:
                parts = post["path"].split("/")
                user_name = parts[1][1:]
                post_num = parts[3]

                if post["private"]:
                    self.log.debug("Skipping @%s/%s (private)",
                                   user_name, post_num)
                    continue
                yield user_name, post_num

            if len(posts) < 30:
                return
            params["offset"] += 30

    def _get_post_data(self, user_name, post_num):
        url = "{}/api/users/{}/works/{}".format(
            self.root, user_name, post_num)
        headers = {"Referer": self.root, "Authorization": "Bearer null"}
        resp = self.request(url, headers=headers).json()
        creator = resp["creator"]
        post = {
            "post_num"         : post_num,
            "post_url"         : self.root + resp["path"],
            "body"             : resp["body"],
            "source_body"      : resp["source_body"],
            "translated_body"  : resp["translated"],
            "completed_at"     : resp["completed_at"],
            "date"             : text.parse_datetime(
                resp["completed_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "nsfw"             : resp["nsfw"],
            "anonymous"        : resp["anonymous"],
            "tags"             : resp["tag_list"],
            "genre"            : resp["genre"],
            "thanks"           : resp["thanks"],
            "source_thanks"    : resp["source_thanks"],
            "translated_thanks": resp["translated_thanks"],
            "creator": {
                "id"           : creator["id"],
                "name"         : creator["name"],
                "screen_name"  : creator["screen_name"],
                "avatar_url"   : creator["avatar_url"],
                "header_url"   : creator["header_url"],
            }
        }
        if not resp["anonymous"] and "client" in resp:
            client = resp["client"]
            post["client"] = {
                "id"           : client["id"],
                "name"         : client["name"],
                "screen_name"  : client["screen_name"],
                "avatar_url"   : client["avatar_url"],
                "header_url"   : client["header_url"],
            }
        return resp, post

    def _get_urls_from_post(self, resp, post):
        if self.thumbnails and "og_image_url" in resp:
            post["content_category"] = "thumb"
            post["file_id"] = "thumb"
            post["file_url"] = resp["og_image_url"]
            yield post

        for preview in resp["previews"]:
            post["content_category"] = "preview"
            post["file_id"] = preview["id"]
            post["file_url"] = preview["url"]
            info = preview["information"]
            post["original"] = {
                "width"     : info["width"],
                "height"    : info["height"],
                "byte_size" : info["byte_size"],
                "duration"  : info["duration"],
                "frame_rate": info["frame_rate"],
                "software"  : info["software"],
                "extension" : info["extension"],
                "is_movie"  : info["is_movie"],
                "transcoder": info["transcoder"],
            }
            yield post


class SkebPostExtractor(SkebExtractor):
    """Extractor for a single skeb post"""
    subcategory = "post"
    pattern = r"(?:https?://)?skeb\.jp/@([^/?#]+)/works/(\d+)"
    test = ("https://skeb.jp/@kanade_cocotte/works/38", {
        "count": 2,
        "keyword": {
            "anonymous": False,
            "body": "re:はじめまして。私はYouTubeにてVTuberとして活動をしている湊ラ",
            "client": {
                "avatar_url": "https://pbs.twimg.com/profile_images"
                              "/1537488326697287680/yNUbLDgC.jpg",
                "header_url": "https://pbs.twimg.com/profile_banners"
                              "/1375007870291300358/1655744756/1500x500",
                "id": 1196514,
                "name": "湊ラギ♦️🎀Vtuber🎀次回6/23予定",
                "screen_name": "minato_ragi",
            },
            "completed_at": "2022-02-27T14:03:45.442Z",
            "content_category": "preview",
            "creator": {
                "avatar_url": "https://pbs.twimg.com/profile_images"
                              "/1225470417063645184/P8_SiB0V.jpg",
                "header_url": "https://pbs.twimg.com/profile_banners"
                              "/71243217/1647958329/1500x500",
                "id": 159273,
                "name": "イチノセ奏",
                "screen_name": "kanade_cocotte",
            },
            "date": "dt:2022-02-27 14:03:45",
            "file_id": int,
            "file_url": str,
            "genre": "art",
            "nsfw": False,
            "original": {
                "byte_size": int,
                "duration": None,
                "extension": "re:psd|png",
                "frame_rate": None,
                "height": 3727,
                "is_movie": False,
                "width": 2810,
            },
            "post_num": "38",
            "post_url": "https://skeb.jp/@kanade_cocotte/works/38",
            "source_body": None,
            "source_thanks": None,
            "tags": list,
            "thanks": None,
            "translated_body": False,
            "translated_thanks": None,
        }
    })

    def __init__(self, match):
        SkebExtractor.__init__(self, match)
        self.post_num = match.group(2)

    def posts(self):
        return ((self.user_name, self.post_num),)


class SkebUserExtractor(SkebExtractor):
    """Extractor for all posts from a skeb user"""
    subcategory = "user"
    pattern = r"(?:https?://)?skeb\.jp/@([^/?#]+)/?$"
    test = ("https://skeb.jp/@kanade_cocotte", {
        "pattern": r"https://skeb\.imgix\.net/uploads/origins/[\w-]+"
                   r"\?bg=%23fff&auto=format&txtfont=bold&txtshad=70"
                   r"&txtclr=BFFFFFFF&txtalign=middle%2Ccenter&txtsize=150"
                   r"&txt=SAMPLE&w=800&s=\w+",
        "range": "1-5",
    })

    def posts(self):
        url = "{}/api/users/{}/works".format(self.root, self.user_name)

        params = {"role": "creator", "sort": "date"}
        posts = self._pagination(url, params)

        if self.config("sent-requests", False):
            params = {"role": "client", "sort": "date"}
            posts = itertools.chain(posts, self._pagination(url, params))

        return posts


class SkebFollowingExtractor(SkebExtractor):
    """Extractor for all creators followed by a skeb user"""
    subcategory = "following"
    pattern = r"(?:https?://)?skeb\.jp/@([^/?#]+)/following_creators"
    test = ("https://skeb.jp/@user/following_creators",)

    def items(self):
        for user in self.users():
            url = "{}/@{}".format(self.root, user["screen_name"])
            user["_extractor"] = SkebUserExtractor
            yield Message.Queue, url, user

    def users(self):
        url = "{}/api/users/{}/following_creators".format(
            self.root, self.user_name)
        headers = {"Referer": self.root, "Authorization": "Bearer null"}
        params = {"sort": "date", "offset": 0, "limit": 90}

        while True:
            data = self.request(url, params=params, headers=headers).json()
            yield from data

            if len(data) < params["limit"]:
                return
            params["offset"] += params["limit"]
