# -*- coding: utf-8 -*-

# Copyright 2016, 2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://seiga.nicovideo.jp"""

from .common import Extractor, Message
from .. import config, exception
from ..cache import cache
from xml.etree import ElementTree


class SeigaExtractor(Extractor):
    """Base class for seiga extractors"""
    category = "seiga"

    def items(self):
        self.login()
        data = self.get_metadata()
        yield Message.Version, 1
        yield Message.Directory, data
        for image in self.get_images():
            data.update(image)
            url = self.get_image_url(image["image-id"])
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
        username = config.interpolate(("extractor", self.category, "username"))
        password = config.interpolate(("extractor", self.category, "password"))
        self.session.cookies = self._login_impl(username, password)

    @cache(maxage=30*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        url = "https://account.nicovideo.jp/api/v1/login"
        params = {"mail_tel": username, "password": password}
        self.session.post(url, data=params).close()
        if "user_session" not in self.session.cookies:
            raise exception.AuthenticationError()
        del self.session.cookies["nicosid"]
        return self.session.cookies


class SeigaUserExtractor(SeigaExtractor):
    """Extractor for images of a user from seiga.nicovideo.jp"""
    subcategory = "user"
    directory_fmt = ["{category}", "{user-id}"]
    filename_fmt = "{category}_{user-id}_{image-id}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.|seiga\.)?nicovideo\.jp/"
                r"user/illust/(\d+)")]
    test = [
        ("http://seiga.nicovideo.jp/user/illust/39537793", {
            "keyword": "2a18eb83fbdadaec6ace5019a7aa7a9a446c6915",
            "content": "40dc3b454d429108cb834b9e449229231010ddfa",
        }),
        ("http://seiga.nicovideo.jp/user/illust/79433", {
            "url": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "keyword": "82b330a4d1e8a2cd47ee934a0a40829232b49cdc",
        }),
    ]

    def __init__(self, match):
        SeigaExtractor.__init__(self)
        self.user_id = match.group(1)

    def get_metadata(self):
        return {"user-id": self.user_id}

    def get_images(self):
        keymap = {0: "image-id", 2: "title", 3: "description",
                  7: "summary", 8: "genre", 18: "date"}
        url = "http://seiga.nicovideo.jp/api/user/data?id=" + self.user_id
        response = self.request(url)
        root = ElementTree.fromstring(response.text)
        if root[0].text == "0":
            return []
        return [
            {
                key: image[index].text
                for index, key in keymap.items()
            }
            for image in root[1]
        ]


class SeigaImageExtractor(SeigaExtractor):
    """Extractor for single images from seiga.nicovideo.jp"""
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{image-id}.{extension}"
    pattern = [(r"(?:https?://)?(?:www\.|seiga\.)?nicovideo\.jp/"
                r"(?:seiga/im|image/source/)(\d+)"),
               (r"(?:https?://)?lohas\.nicoseiga\.jp/"
                r"(?:priv|o)/[^/]+/\d+/(\d+)")]
    test = [
        ("http://seiga.nicovideo.jp/seiga/im5977527", {
            "keyword": "12bbef9aef772a74681608fb1b3f0b17c180a47e",
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
        return ({"image-id": self.image_id},)
