# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mike Fährmann
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
    directory_fmt = ["{category}", "{user_id}"]
    filename_fmt = "{category}_{artist_id}_{image_id}_p{index:>02}.{extension}"
    archive_fmt = "{image_id}_{index}"
    cookiedomain = "nijie.info"
    root = "https://nijie.info"
    view_url = "https://nijie.info/view.php?id="
    popup_url = "https://nijie.info/view_popup.php?id="

    def __init__(self, match=None):
        AsynchronousExtractor.__init__(self)
        self.session.headers["Referer"] = self.root + "/"
        self.user_id = match.group(1) if match else None

    def items(self):
        self.login()
        data = self.get_job_metadata()

        yield Message.Version, 1
        yield Message.Directory, data

        for image_id in self.get_image_ids():
            for image_url, image_data in self.get_image_data(image_id):
                image_data.update(data)
                if not image_data["extension"]:
                    image_data["extension"] = "jpg"
                yield Message.Url, image_url, image_data

    def get_job_metadata(self):
        """Collect metadata for extractor-job"""
        return {"user_id": text.parse_int(self.user_id)}

    def get_image_ids(self):
        """Collect all relevant image-ids"""

    def get_image_data(self, image_id):
        """Get URL and metadata for images specified by 'image_id'"""
        page = self.request(self.view_url + image_id).text
        return self.extract_image_data(page, image_id)

    def extract_image_data(self, page, image_id):
        """Get URL and metadata for images from 'page'"""
        title, pos = text.extract(
            page, '<meta property="og:title" content="', '"')
        description, pos = text.extract(
            page, '<meta property="og:description" content="', '"', pos)
        artist_id, pos = text.extract(
            page, '"sameAs": "https://nijie.info/members.php?id=', '"', pos)
        images = list(text.extract_iter(
            page, '<a href="./view_popup.php', '</a>', pos))

        title = title.rpartition("|")[0].strip()
        image_id = text.parse_int(image_id)
        artist_id = text.parse_int(artist_id)

        for index, image in enumerate(images):
            url = "https:" + text.extract(image, 'src="', '"')[0]
            url = url.replace("/__rs_l120x120/", "/", 1)

            yield url, text.nameext_from_url(url, {
                "index": index,
                "count": len(images),
                "title": title,
                "description": description,
                "image_id": image_id,
                "artist_id": artist_id,
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
        page = self.request(
            self.root + "/login_int.php", method="POST", data=data).text
        if "//nijie.info/login.php" in page:
            raise exception.AuthenticationError()
        return self.session.cookies

    def _pagination(self, path):
        url = "{}/{}.php".format(self.root, path)
        params = {"id": self.user_id, "p": 1}

        while True:
            response = self.request(url, params=params, expect=(404,))
            if response.status_code == 404:
                raise exception.NotFoundError("artist")

            page = response.text
            ids = list(text.extract_iter(page, ' illust_id="', '"'))
            yield from ids

            if '<a rel="next"' not in page:
                return
            params["p"] += 1


class NijieUserExtractor(NijieExtractor):
    """Extractor for works of a nijie-user"""
    subcategory = "user"
    pattern = [(r"(?:https?://)?(?:www\.)?nijie\.info"
                r"/members(?:_illust)?\.php\?id=(\d+)")]
    test = [
        ("https://nijie.info/members_illust.php?id=44", {
            "url": "585d821df4716b1098660a0be426d01db4b65f2a",
            "keyword": "1eb3387196f1f30d6d74a41f4c77faaadd588e52",
        }),
        ("https://nijie.info/members_illust.php?id=43", {
            "exception": exception.NotFoundError,
        }),
        ("https://nijie.info/members.php?id=44", None),
    ]

    def get_image_ids(self):
        return self._pagination("members_illust")


class NijieDoujinExtractor(NijieExtractor):
    """Extractor for doujin entries of a nijie-user"""
    subcategory = "doujin"
    pattern = [(r"(?:https?://)?(?:www\.)?nijie\.info/"
                r"members_dojin\.php\?id=(\d+)")]
    test = [
        ("https://nijie.info/members_dojin.php?id=6782", {
            "count": ">= 18",
        }),
    ]

    def get_image_ids(self):
        return self._pagination("members_dojin")


class NijieFavoriteExtractor(NijieExtractor):
    """Extractor for all favorites/bookmarks of a nijie-user"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "bookmarks", "{user_id}"]
    archive_fmt = "f_{user_id}_{image_id}_{index}"
    pattern = [(r"(?:https?://)?(?:www\.)?nijie\.info"
                r"/user_like_illust_view\.php\?id=(\d+)")]
    test = [
        ("https://nijie.info/user_like_illust_view.php?id=44", {
            "count": ">= 16",
        }),
    ]

    def get_image_ids(self):
        return self._pagination("user_like_illust_view")


class NijieImageExtractor(NijieExtractor):
    """Extractor for a work/image from nijie.info"""
    subcategory = "image"
    pattern = [r"(?:https?://)?(?:www\.)?nijie\.info"
               r"/view(?:_popup)?\.php\?id=(\d+)"]
    test = [
        ("https://nijie.info/view.php?id=70720", {
            "url": "a10d4995645b5f260821e32c60a35f73546c2699",
            "keyword": "0728fc3bbef1e192abfd59f88f07921d3d336804",
            "content": "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",
        }),
        ("https://nijie.info/view.php?id=70724", {
            "exception": exception.NotFoundError,
        }),
        ("https://nijie.info/view_popup.php?id=70720", None),
    ]

    def __init__(self, match):
        NijieExtractor.__init__(self)
        self.image_id = match.group(1)
        self.page = ""

    def get_job_metadata(self):
        response = self.request(self.view_url + self.image_id, expect=(404,))
        if response.status_code == 404:
            raise exception.NotFoundError("image")
        self.page = response.text
        self.user_id = text.extract(
            self.page, '"sameAs": "https://nijie.info/members.php?id=', '"')[0]
        return NijieExtractor.get_job_metadata(self)

    def get_image_ids(self):
        return (self.image_id,)

    def get_image_data(self, _):
        return self.extract_image_data(self.page, self.image_id)
