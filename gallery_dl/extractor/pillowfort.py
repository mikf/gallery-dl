# -*- coding: utf-8 -*-

# Copyright 2021-2023 Mike Fährmann
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
    cookies_domain = "www.pillowfort.social"

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
            post["count"] = len(files)
            yield Message.Directory, post

            post["num"] = 0
            for file in files:
                url = file["url"] or file.get("b2_lg_url")
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
        if self.cookies.get("_Pf_new_session", domain=self.cookies_domain):
            return
        if self.cookies.get("remember_user_token", domain=self.cookies_domain):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=14*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "https://www.pillowfort.social/users/sign_in"
        page = self.request(url).text
        auth = text.extr(page, 'name="authenticity_token" value="', '"')

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
    example = "https://www.pillowfort.social/posts/12345"

    def posts(self):
        url = "{}/posts/{}/json/".format(self.root, self.item)
        return (self.request(url).json(),)


class PillowfortUserExtractor(PillowfortExtractor):
    """Extractor for all posts of a pillowfort user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"/(?!posts/)([^/?#]+(?:/tagged/[^/?#]+)?)"
    example = "https://www.pillowfort.social/USER"

    def posts(self):
        url = "{}/{}/json/".format(self.root, self.item)
        params = {"p": 1}

        while True:
            posts = self.request(url, params=params).json()["posts"]
            yield from posts

            if len(posts) < 20:
                return
            params["p"] += 1
