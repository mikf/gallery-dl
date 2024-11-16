# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vipergirls.to/"""

from xml.etree import ElementTree as ET

from .. import exception
from .. import text
from .. import util
from ..cache import cache
from .common import Extractor
from .common import Message

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
        domain = self.config("domain")
        if domain:
            self.root = text.ensure_http_scheme(domain)

    def items(self):
        self.login()
        posts = self.posts()

        like = self.config("like")
        if like:
            user_hash = posts[0].get("hash")
            if len(user_hash) < 16:
                self.log.warning("Login required to like posts")
                like = False

        posts = posts.iter("post")
        if self.page:
            util.advance(posts, (text.parse_int(self.page[5:]) - 1) * 15)

        for post in posts:
            data = post.attrib
            data["thread_id"] = self.thread_id

            yield Message.Directory, data

            image = None
            for image in post:
                yield Message.Queue, image.attrib["main_url"], data

            if image is not None and like:
                self.like(post, user_hash)

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=90 * 86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = f"{self.root}/login.php?do=login"
        data = {
            "vb_login_username": username,
            "vb_login_password": password,
            "do": "login",
            "cookieuser": "1",
        }

        response = self.request(url, method="POST", data=data)
        if not response.cookies.get("vg_password"):
            raise exception.AuthenticationError()

        return {cookie.name: cookie.value for cookie in response.cookies}

    def like(self, post, user_hash):
        url = self.root + "/post_thanks.php"
        params = {
            "do": "post_thanks_add",
            "p": post.get("id"),
            "securitytoken": user_hash,
        }

        with self.request(url, params=params, allow_redirects=False):
            pass


class VipergirlsThreadExtractor(VipergirlsExtractor):
    """Extractor for vipergirls threads"""

    subcategory = "thread"
    pattern = BASE_PATTERN + r"/threads/(\d+)(?:-[^/?#]+)?(/page\d+)?(?:$|#|\?(?!p=))"
    example = "https://vipergirls.to/threads/12345-TITLE"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.page = match.groups()

    def posts(self):
        url = f"{self.root}/vr.php?t={self.thread_id}"
        return ET.fromstring(self.request(url).text)


class VipergirlsPostExtractor(VipergirlsExtractor):
    """Extractor for vipergirls posts"""

    subcategory = "post"
    pattern = BASE_PATTERN + r"/threads/(\d+)(?:-[^/?#]+)?\?p=\d+[^#]*#post(\d+)"
    example = "https://vipergirls.to/threads/12345-TITLE?p=23456#post23456"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.post_id = match.groups()
        self.page = 0

    def posts(self):
        url = f"{self.root}/vr.php?p={self.post_id}"
        return ET.fromstring(self.request(url).text)
