# -*- coding: utf-8 -*-

# Copyright 2023-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vipergirls.to/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vipergirls\.to"


class VipergirlsExtractor(Extractor):
    """Base class for vipergirls extractors"""
    category = "vipergirls"
    root = "https://vipergirls.to"
    request_interval = 0.5
    request_interval_min = 0.2
    cookies_domain = ".vipergirls.to"
    cookies_names = ("vg_userid", "vg_password")

    def _init(self):
        if domain := self.config("domain"):
            pos = domain.find("://")
            if pos >= 0:
                self.root = domain.rstrip("/")
                self.cookies_domain = "." + domain[pos+1:].strip("/")
            else:
                domain = domain.strip("/")
                self.root = "https://" + domain
                self.cookies_domain = "." + domain
        else:
            self.root = "https://viper.click"
            self.cookies_domain = ".viper.click"

    def items(self):
        self.login()
        root = self.posts()
        forum_title = root[1].attrib["title"]
        thread_title = root[2].attrib["title"]

        if like := self.config("like"):
            user_hash = root[0].get("hash")
            if len(user_hash) < 16:
                self.log.warning("Login required to like posts")
                like = False

        posts = root.iter("post")
        if (order := self.config("order-posts")) and \
                order[0] not in ("d", "r"):
            if self.page:
                util.advance(posts, (text.parse_int(self.page[5:]) - 1) * 15)
        else:
            posts = list(posts)
            if self.page:
                offset = text.parse_int(self.page[5:]) * 15
                posts = posts[:offset]
            posts.reverse()

        for post in posts:
            images = list(post)

            data = post.attrib
            data["forum_title"] = forum_title
            data["thread_id"] = self.thread_id
            data["thread_title"] = thread_title
            data["post_id"] = data.pop("id")
            data["post_num"] = data.pop("number")
            data["post_title"] = data.pop("title")
            data["count"] = len(images)
            del data["imagecount"]

            yield Message.Directory, "", data
            if images:
                for data["num"], image in enumerate(images, 1):
                    yield Message.Queue, image.attrib["main_url"], data
                if like:
                    self.like(post, user_hash)

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = f"{self.root}/login.php?do=login"
        data = {
            "vb_login_username": username,
            "vb_login_password": password,
            "do"               : "login",
            "cookieuser"       : "1",
        }

        response = self.request(url, method="POST", data=data)
        if not response.cookies.get("vg_password"):
            raise exception.AuthenticationError()

        return {cookie.name: cookie.value
                for cookie in response.cookies}

    def like(self, post, user_hash):
        url = self.root + "/post_thanks.php"
        params = {
            "do"           : "post_thanks_add",
            "p"            : post.get("id"),
            "securitytoken": user_hash,
        }

        with self.request(url, params=params, allow_redirects=False):
            pass


class VipergirlsThreadExtractor(VipergirlsExtractor):
    """Extractor for vipergirls threads"""
    subcategory = "thread"
    pattern = (rf"{BASE_PATTERN}"
               rf"/threads/(\d+)(?:-[^/?#]+)?(/page\d+)?(?:$|#|\?(?!p=))")
    example = "https://vipergirls.to/threads/12345-TITLE"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.page = match.groups()

    def posts(self):
        url = f"{self.root}/vr.php?t={self.thread_id}"
        return self.request_xml(url)


class VipergirlsPostExtractor(VipergirlsExtractor):
    """Extractor for vipergirls posts"""
    subcategory = "post"
    pattern = (rf"{BASE_PATTERN}"
               rf"/threads/(\d+)(?:-[^/?#]+)?\?p=\d+[^#]*#post(\d+)")
    example = "https://vipergirls.to/threads/12345-TITLE?p=23456#post23456"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.post_id = match.groups()
        self.page = 0

    def posts(self):
        url = f"{self.root}/vr.php?p={self.post_id}"
        return self.request_xml(url)
