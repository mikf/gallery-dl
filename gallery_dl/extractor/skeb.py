# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://skeb.jp/"""

from .common import Extractor, Message
from .. import text


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
        for post_num in self.posts():
            response, post = self._get_post_data(post_num)
            yield Message.Directory, post
            for data in self._get_urls_from_post(response, post):
                url = data["file_url"]
                yield Message.Url, url, text.nameext_from_url(url, data)

    def posts(self):
        """Return post number"""

    def _pagination(self):
        url = "{}/api/users/{}/works".format(self.root, self.user_name)
        params = {"role": "creator", "sort": "date", "offset": 0}
        headers = {"Referer": self.root, "Authorization": "Bearer null"}

        while True:
            posts = self.request(url, params=params, headers=headers).json()

            for post in posts:
                post_num = post["path"].rpartition("/")[2]
                if post["private"]:
                    self.log.debug("Skipping %s (private)", post_num)
                    continue
                yield post_num

            if len(posts) < 30:
                return
            params["offset"] += 30

    def _get_post_data(self, post_num):
        url = "{}/api/users/{}/works/{}".format(
            self.root, self.user_name, post_num)
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

    def __init__(self, match):
        SkebExtractor.__init__(self, match)
        self.post_num = match.group(2)

    def posts(self):
        return (self.post_num,)


class SkebUserExtractor(SkebExtractor):
    """Extractor for all posts from a skeb user"""
    subcategory = "user"
    pattern = r"(?:https?://)?skeb\.jp/@([^/?#]+)"

    def posts(self):
        return self._pagination()
