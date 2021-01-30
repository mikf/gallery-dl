# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pillowfort.social/"""

from .common import Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?www\.pillowfort\.social"


class PillowfortExtractor(Extractor):
    """Base class for pillowfort extractors"""
    category = "pillowfort"
    root = "https://www.pillowfort.social"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = ("{post_id} {title|original_post[title]} "
                    "{num:>02}.{extension}")
    archive_fmt = "{id}"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)
        self.reblogs = self.config("reblogs", False)

    def items(self):
        for post in self.posts():

            if "original_post" in post and not self.reblogs:
                continue

            files = post["media"]
            del post["media"]

            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
            yield Message.Directory, post

            post["num"] = 0
            for file in files:
                url = file["url"]
                if url:
                    post.update(file)
                    post["num"] += 1
                    post["date"] = text.parse_datetime(
                        file["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    yield Message.Url, url, text.nameext_from_url(url, post)


class PillowfortPostExtractor(PillowfortExtractor):
    """Extractor for a single pillowfort post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = ("https://www.pillowfort.social/posts/27510", {
        "pattern": r"https://img\d+\.pillowfort\.social/posts/\w+_out\d+\.png",
        "count": 4,
        "keyword": {
            "avatar_url": str,
            "col": 0,
            "commentable": True,
            "comments_count": int,
            "community_id": None,
            "content": str,
            "created_at": str,
            "date": "type:datetime",
            "deleted": None,
            "deleted_at": None,
            "deleted_by_mod": None,
            "deleted_for_flag_id": None,
            "embed_code": None,
            "id": int,
            "last_activity": str,
            "last_activity_elapsed": str,
            "last_edited_at": None,
            "likes_count": int,
            "media_type": "picture",
            "nsfw": False,
            "num": int,
            "original_post_id": None,
            "original_post_user_id": None,
            "picture_content_type": None,
            "picture_file_name": None,
            "picture_file_size": None,
            "picture_updated_at": None,
            "post_id": 27510,
            "post_type": "picture",
            "privacy": "public",
            "reblog_copy_info": list,
            "rebloggable": True,
            "reblogged_from_post_id": None,
            "reblogged_from_user_id": None,
            "reblogs_count": int,
            "row": int,
            "small_image_url": None,
            "tags": list,
            "time_elapsed": str,
            "timestamp": str,
            "title": "What is Pillowfort.io? ",
            "updated_at": str,
            "url": r"re:https://img3.pillowfort.social/posts/.*\.png",
            "user_id": 5,
            "username": "Staff"
        },
    })

    def posts(self):
        url = "{}/posts/{}/json/".format(self.root, self.item)
        return (self.request(url).json(),)


class PillowfortUserExtractor(PillowfortExtractor):
    """Extractor for all posts of a pillowfort user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!posts/)([^/?#]+)"
    test = ("https://www.pillowfort.social/Pome", {
        "pattern": r"https://img\d+\.pillowfort\.social/posts/",
        "range": "1-15",
        "count": 15,
    })

    def posts(self):
        url = "{}/{}/json/".format(self.root, self.item)
        params = {"p": 1}

        while True:
            posts = self.request(url, params=params).json()["posts"]
            yield from posts

            if len(posts) < 20:
                return
            params["p"] += 1
