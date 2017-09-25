# -*- coding: utf-8 -*-

# Copyright 2015-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nijie.info/"""

from .common import AsynchronousExtractor, Message
from .. import text, exception
from ..cache import cache


class NijieExtractor(AsynchronousExtractor):
    """Base class for nijie extractors"""
    category = "nijie"
    directory_fmt = ["{category}", "{artist_id}"]
    filename_fmt = "{category}_{artist_id}_{image_id}_p{index:>02}.{extension}"
    cookiedomain = "nijie.info"
    popup_url = "https://nijie.info/view_popup.php?id="

    def __init__(self):
        AsynchronousExtractor.__init__(self)
        self.session.headers["Referer"] = "https://nijie.info/"
        self.artist_id = ""

    def items(self):
        self.login()
        data = self.get_job_metadata()
        images = self.get_image_ids()
        yield Message.Version, 1
        yield Message.Directory, data
        for image_id in images:
            for image_url, image_data in self.get_image_data(image_id):
                image_data.update(data)
                yield Message.Url, image_url, image_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {"artist_id": self.artist_id}

    def get_image_ids(self):
        """Collect all image-ids for a specific artist"""
        return []

    def get_image_data(self, image_id):
        """Get URL and metadata for images specified by 'image_id'"""
        page = self.request(self.popup_url + image_id).text
        return self.extract_image_data(page, image_id)

    @staticmethod
    def extract_image_data(page, image_id):
        """Get URL and metadata for images from 'page'"""
        images = list(text.extract_iter(page, '<img src="//pic', '"'))
        for index, url in enumerate(images):
            yield "https://pic" + url, text.nameext_from_url(url, {
                "count": len(images),
                "index": index,
                "image_id": image_id,
            })

    def login(self):
        """Login and obtain session cookie"""
        if not self._check_cookies(("nemail", "nlogin")):
            username, password = self._get_auth_info()
            self.session.cookies = self._login_impl(username, password)

    @cache(maxage=30*24*60*60, keyarg=1)
    def _login_impl(self, username, password):
        """Actual login implementation"""
        self.log.info("Logging in as %s", username)
        data = {"email": username, "password": password}
        page = self.request("https://nijie.info/login_int.php",
                            method="POST", data=data).text
        if "//nijie.info/login.php" in page:
            raise exception.AuthenticationError()
        return self.session.cookies


class NijieUserExtractor(NijieExtractor):
    """Extractor for works of a nijie-user"""
    subcategory = "user"
    pattern = [(r"(?:https?://)?(?:www\.)?nijie\.info/"
                r"members(?:_illust)?\.php\?id=(\d+)")]
    test = [
        ("https://nijie.info/members_illust.php?id=44", {
            "url": "585d821df4716b1098660a0be426d01db4b65f2a",
            "keyword": "804d3a9bb8205048ac0d1fe8eec39266b50f1e8e",
        }),
        ("https://nijie.info/members_illust.php?id=43", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        NijieExtractor.__init__(self)
        self.artist_id = match.group(1)

    def get_image_ids(self):
        params = {"id": self.artist_id, "p": 1}
        url = "https://nijie.info/members_illust.php"
        while True:
            response = self.request(url, params=params, fatal=False)
            if response.status_code == 404:
                raise exception.NotFoundError("artist")
            ids = list(text.extract_iter(response.text, ' illust_id="', '"'))
            yield from ids
            if len(ids) < 48:
                return
            params["p"] += 1


class NijieImageExtractor(NijieExtractor):
    """Extractor for a work/image from nijie.info"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?nijie\.info/view\.php\?id=(\d+)"]
    test = [
        ("https://nijie.info/view.php?id=70720", {
            "url": "a10d4995645b5f260821e32c60a35f73546c2699",
            "keyword": "4ecfd46460761b7a89fdba815eece10e917032c2",
            "content": "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",
        }),
        ("https://nijie.info/view.php?id=70724", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        NijieExtractor.__init__(self)
        self.image_id = match.group(1)
        self.page = ""

    def get_job_metadata(self):
        response = self.request(self.popup_url + self.image_id,
                                allow_redirects=False, allow_empty=True)
        if 300 <= response.status_code < 400:
            raise exception.NotFoundError("image")
        self.page = response.text
        self.artist_id = text.extract(self.page, "/nijie_picture/sp/", "_")[0]
        return NijieExtractor.get_job_metadata(self)

    def get_image_ids(self):
        return (self.image_id,)

    def get_image_data(self, _):
        return self.extract_image_data(self.page, self.image_id)
