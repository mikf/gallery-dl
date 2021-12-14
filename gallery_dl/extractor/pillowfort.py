# -*- coding: utf-8 -*-

# Copyright 2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pillowfort.social/"""

from .common import Extractor, Message
from ..cache import cache
from .. import text, exception
import re

BASE_PATTERN = r"(?:https?://)?www\.pillowfort\.social"


class PillowfortExtractor(Extractor):
    """Base class for pillowfort extractors"""
    category = "pillowfort"
    root = "https://www.pillowfort.social"
    directory_fmt = ("{category}", "{username}")
    filename_fmt = ("{post_id} {title|original_post[title]:?/ /}"
                    "{num:>02}.{extension}")
    archive_fmt = "{id}"
    cookiedomain = "www.pillowfort.social"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.item = match.group(1)

    def items(self):
        self.login()
        inline = self.config("inline", True)
        reblogs = self.config("reblogs", False)
        external = self.config("external", False)

        if inline:
            inline = re.compile(r'src="(https://img\d+\.pillowfort\.social'
                                r'/posts/[^"]+)').findall

        for post in self.posts():
            if "original_post" in post and not reblogs:
                continue

            files = post.pop("media")
            if inline:
                for url in inline(post["content"]):
                    files.append({"url": url})

            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
            post["post_id"] = post.pop("id")
            yield Message.Directory, post

            post["num"] = 0
            for file in files:
                url = file["url"]
                if not url:
                    continue

                if file.get("embed_code"):
                    if not external:
                        continue
                    msgtype = Message.Queue
                else:
                    post["num"] += 1
                    msgtype = Message.Url

                post.update(file)
                text.nameext_from_url(url, post)
                post["hash"], _, post["filename"] = \
                    post["filename"].partition("_")

                if "id" not in file:
                    post["id"] = post["hash"]
                if "created_at" in file:
                    post["date"] = text.parse_datetime(
                        file["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

                yield msgtype, url, post

    def login(self):
        cget = self.session.cookies.get
        if cget("_Pf_new_session", domain=self.cookiedomain) \
                or cget("remember_user_token", domain=self.cookiedomain):
            return

        username, password = self._get_auth_info()
        if username:
            cookies = self._login_impl(username, password)
            self._update_cookies(cookies)

    @cache(maxage=14*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://www.pillowfort.social/users/sign_in"
        page = self.request(url).text
        auth = text.extract(page, 'name="authenticity_token" value="', '"')[0]

        headers = {"Origin": self.root, "Referer": url}
        data = {
            "utf8"              : "✓",
            "authenticity_token": auth,
            "user[email]"       : username,
            "user[password]"    : password,
            "user[remember_me]" : "1",
        }
        response = self.request(url, method="POST", headers=headers, data=data)

        if not response.history:
            raise exception.AuthenticationError()

        return {
            cookie.name: cookie.value
            for cookie in response.history[0].cookies
        }


class PillowfortPostExtractor(PillowfortExtractor):
    """Extractor for a single pillowfort post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = (
        ("https://www.pillowfort.social/posts/27510", {
            "pattern": r"https://img\d+\.pillowfort\.social"
                       r"/posts/\w+_out\d+\.png",
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
        }),
        ("https://www.pillowfort.social/posts/1557500", {
            "options": (("external", True), ("inline", False)),
            "pattern": r"https://twitter\.com/Aliciawitdaart/status"
                       r"/1282862493841457152",
        }),
        ("https://www.pillowfort.social/posts/1672518", {
            "options": (("inline", True),),
            "count": 3,
        }),
    )

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
