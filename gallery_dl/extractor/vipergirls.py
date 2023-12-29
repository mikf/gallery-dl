# -*- coding: utf-8 -*-

# Copyright 2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://vipergirls.to/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache

from xml.etree import ElementTree

BASE_PATTERN = r"(?:https?://)?(?:www\.)?vipergirls\.to"


class VipergirlsExtractor(Extractor):
    """Base class for vipergirls extractors"""
    category = "vipergirls"
    root = "https://vipergirls.to"
    request_interval = 0.5
    request_interval_min = 0.2
    cookies_domain = ".vipergirls.to"
    cookies_names = ("vg_userid", "vg_password")

    def items(self):
        self.login()

        for post in self.posts():
            data = post.attrib
            data["thread_id"] = self.thread_id

            yield Message.Directory, data
            for image in post:
                yield Message.Queue, image.attrib["main_url"], data

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            self.cookies_update(self._login_impl(username, password))

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "{}/login.php?do=login".format(self.root)
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


class VipergirlsThreadExtractor(VipergirlsExtractor):
    """Extractor for vipergirls threads"""
    subcategory = "thread"
    pattern = BASE_PATTERN + r"/threads/(\d+)(?:-[^/?#]+)?(/page\d+)?$"
    example = "https://vipergirls.to/threads/12345-TITLE"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.page = match.groups()

    def posts(self):
        url = "{}/vr.php?t={}".format(self.root, self.thread_id)
        root = ElementTree.fromstring(self.request(url).text)
        posts = root.iter("post")

        if self.page:
            util.advance(posts, (text.parse_int(self.page[5:]) - 1) * 15)
        return posts


class VipergirlsPostExtractor(VipergirlsExtractor):
    """Extractor for vipergirls posts"""
    subcategory = "post"
    pattern = (BASE_PATTERN +
               r"/threads/(\d+)(?:-[^/?#]+)?\?p=\d+[^#]*#post(\d+)")
    example = "https://vipergirls.to/threads/12345-TITLE?p=23456#post23456"

    def __init__(self, match):
        VipergirlsExtractor.__init__(self, match)
        self.thread_id, self.post_id = match.groups()

    def posts(self):
        url = "{}/vr.php?p={}".format(self.root, self.post_id)
        root = ElementTree.fromstring(self.request(url).text)
        return root.iter("post")
