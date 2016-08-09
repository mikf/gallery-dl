# -*- coding: utf-8 -*-

# Copyright 2016 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from http://seiga.nicovideo.jp"""

from .common import Extractor, Message
from .. import config, exception
from ..cache import cache

class SeigaImageExtractor(Extractor):
    """Extract a single image from seiga.nicovideo.jp"""
    category = "seiga"
    subcategory = "image"
    directory_fmt = ["{category}"]
    filename_fmt = "{category}_{image-id}.jpg"
    pattern = [r"(?:https?://)?(?:www\.|seiga\.)?nicovideo\.jp/seiga/im(\d+)"]
    test = [("http://seiga.nicovideo.jp/seiga/im5977527", {
        "keyword": "e2ea59186c47beb71484ba35d550cf6511ac185a",
        "content": "d9202292012178374d57fb0126f6124387265297",
    })]

    def __init__(self, match):
        Extractor.__init__(self)
        self.image_id = match.group(1)

    def items(self):
        self.session.cookies = self.login(
            config.interpolate(("extractor", self.category, "username")),
            config.interpolate(("extractor", self.category, "password")),
        )
        data = self.get_job_metadata()
        url  = self.get_image_url(self.image_id)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {
            "category": self.category,
            "image-id": self.image_id,
        }

    def get_image_url(self, image_id):
        """Get url for an image with id 'image_id'"""
        url = "http://seiga.nicovideo.jp/image/source/" + image_id
        response = self.session.head(url)
        return response.headers["Location"].replace("/o/", "/priv/", 1)

    @cache(maxage=30*24*60*60, keyarg=1)
    def login(self, username, password):
        """Login and obtain session cookie"""
        url = "https://account.nicovideo.jp/api/v1/login"
        params = {"mail_tel": username, "password": password}
        self.session.post(url, data=params).close()
        if "user_session" not in self.session.cookies:
            raise exception.AuthenticationError()
        del self.session.cookies["nicosid"]
        return self.session.cookies
