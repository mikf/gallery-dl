# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://seiga.nicovideo.jp"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache


class SeigaExtractor(Extractor):
    """Base class for seiga extractors"""
    category = "seiga"
    cookiedomain = ".nicovideo.jp"

    def items(self):
        self.login()
        data = self.get_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for image in self.get_images():
            data.update(image)
            data["extension"] = None
            url = self.get_image_url(image["image_id"])
            yield Message.Url, url, data

    def get_metadata(self):
        """Collect metadata for extractor-job"""
        return {}

    def get_images(self):
        """Return list of images"""
        return []

    def get_image_url(self, image_id):
        """Get url for an image with id 'image_id'"""
        url = "http://seiga.nicovideo.jp/image/source/" + image_id
        response = self.session.head(url)
        if response.status_code == 404:
            raise exception.NotFoundError("image")
        return response.headers["Location"].replace("/o/", "/priv/", 1)

    def login(self):
        """Login and set necessary cookies"""
        if not self._check_cookies(("user_session",)):
            username, password = self._get_auth_info()
            self.session.cookies = self._login_impl(username, password)

    @cache(maxage=7*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)
        url = "https://account.nicovideo.jp/api/v1/login"
        data = {"mail_tel": username, "password": password}
        self.request(url, method="POST", data=data)
        if "user_session" not in self.session.cookies:
            raise exception.AuthenticationError()
        del self.session.cookies["nicosid"]
        return self.session.cookies


class SeigaUserExtractor(SeigaExtractor):
    """Extractor for images of a user from seiga.nicovideo.jp"""
    subcategory = "user"
    directory_fmt = ["{category}", "{user_id}"]
    filename_fmt = "{category}_{user_id}_{image_id}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.|seiga\.)?nicovideo\.jp/"
                r"user/illust/(\d+)")]
    test = [
        ("http://seiga.nicovideo.jp/user/illust/39537793", {
            "pattern": r"https://lohas\.nicoseiga\.jp/priv/[0-9a-f]+/\d+/\d+",
            "count": 2,
        }),
        ("http://seiga.nicovideo.jp/user/illust/79433", {
            "url": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "count": 0,
        }),
    ]

    def __init__(self, match):
        SeigaExtractor.__init__(self)
        self.user_id = match.group(1)

    def get_metadata(self):
        return {"user_id": self.user_id}

    def get_images(self):
        url = "http://seiga.nicovideo.jp/user/illust/" + self.user_id
        params = {"target": "illust_all", "page": 1}

        while True:
            cnt = 0
            page = self.request(url, params=params).text

            for info in text.extract_iter(
                    page, '<li class="list_item', '</a></li> '):
                yield text.extract_all(info, (
                    ("image_id", '/seiga/im', '"'),
                    ("title"   , '<li class="title">', '</li>'),
                    ("views"   , '</span>', '</li>'),
                    ("comments", '</span>', '</li>'),
                    ("clips"   , '</span>', '</li>'),
                ))[0]
                cnt += 1

            if cnt < 40:
                return
            params["page"] += 1


class SeigaImageExtractor(SeigaExtractor):
    """Extractor for single images from seiga.nicovideo.jp"""
    subcategory = "image"
    filename_fmt = "{category}_{image_id}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.|seiga\.)?nicovideo\.jp/"
                r"(?:seiga/im|image/source/)(\d+)"),
               (r"(?:https?://)?lohas\.nicoseiga\.jp/"
                r"(?:priv|o)/[^/]+/\d+/(\d+)")]
    test = [
        ("http://seiga.nicovideo.jp/seiga/im5977527", {
            "keyword": "6ff7564b35890e333ff7413cb633ddb58339912f",
            "content": "d9202292012178374d57fb0126f6124387265297",
        }),
        ("http://seiga.nicovideo.jp/seiga/im123", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        SeigaExtractor.__init__(self)
        self.image_id = match.group(1)

    def get_images(self):
        return ({"image_id": self.image_id},)
