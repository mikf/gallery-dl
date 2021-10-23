# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
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
    
    def items(self):
        for post_num in self.posts():
            response, post = self._get_post_data(post_num)
            yield Message.Directory, post
            for url, url_data in self._get_urls_from_post(response, post):
                url_data["file_url"] = url
                yield Message.Url, url, url_data
    
    def posts(self):
        """Return post number"""
    
    def _pagination(self):
        url = "{}/api/users/{}/works".format(self.root, self.user_name)
        params = {"role": "creator", "sort": "date", "offset": 0}
        headers = {"Referer": self.root, "Authorization": "Bearer null"}
        
        while True:
            posts = self.request(url, params=params, headers=headers).json()
            
            for post in posts:
                post_num = post["path"].split("/")[-1]
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
        post = {
            "post_num": post_num,
            "post_url": self.root + resp["path"],
            "body": resp["body"],
            "source_body": resp["source_body"],
            "translated_body": resp["translated"],
            "completed_at": resp["completed_at"],
            "date": text.parse_datetime(
                resp["completed_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            "nsfw": resp["nsfw"],
            "anonymous": resp["anonymous"],
            "tags": resp["tag_list"],
            "genre": resp["genre"],
            "thanks": resp["thanks"],
            "source_thanks": resp["source_thanks"],
            "translated_thanks": resp["translated_thanks"],
            "creator": {
                "id": resp["creator"]["id"],
                "name": resp["creator"]["name"],
                "screen_name": resp["creator"]["screen_name"],
                "avatar_url": resp["creator"]["avatar_url"],
                "header_url": resp["creator"]["header_url"],
            }
        }
        if not resp["anonymous"] and "client" in resp:
            post["client"] = {
                "id": resp["client"]["id"],
                "name": resp["client"]["name"],
                "screen_name": resp["client"]["screen_name"],
                "avatar_url": resp["client"]["avatar_url"],
                "header_url": resp["client"]["header_url"],
            }
        return resp, post
    
    def _get_urls_from_post(self, resp, post):
        if "og_image_url" in resp:
            post["content_category"] = "thumb"
            post["file_id"] = "thumb"
            post["extension"] = None
            post["filename"] = text.nameext_from_url(resp["og_image_url"])["filename"]
            yield resp["og_image_url"], post
        
        for preview in resp["previews"]:
            post["content_category"] = "preview"
            post["file_id"] = preview["id"]
            post["extension"] = None
            post["filename"] = text.nameext_from_url(preview["url"])["filename"]
            post["original"] = {
                "width": preview["information"]["width"],
                "height": preview["information"]["height"],
                "byte_size": preview["information"]["byte_size"],
                "duration": preview["information"]["duration"],
                "frame_rate": preview["information"]["frame_rate"],
                "software": preview["information"]["software"],
                "extension": preview["information"]["extension"],
                "is_movie": preview["information"]["is_movie"],
                "transcoder": preview["information"]["transcoder"],
            }
            yield preview["url"], post


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
    
    def __init__(self, match):
        SkebExtractor.__init__(self, match)
    
    def posts(self):
        return self._pagination()
