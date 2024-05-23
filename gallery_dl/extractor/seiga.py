# -*- coding: utf-8 -*-

# Copyright 2016-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://seiga.nicovideo.jp/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache


class SeigaExtractor(Extractor):
    """Base class for seiga extractors"""
    category = "seiga"
    archive_fmt = "{image_id}"
    cookies_domain = ".nicovideo.jp"
    cookies_names = ("user_session",)
    root = "https://seiga.nicovideo.jp"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.start_image = 0

    def items(self):
        self.login()

        images = iter(self.get_images())
        data = next(images)

        yield Message.Directory, data
        for image in util.advance(images, self.start_image):
            data.update(image)
            data["extension"] = None
            yield Message.Url, self.get_image_url(data["image_id"]), data

    def get_images(self):
        """Return iterable containing metadata and images"""

    def get_image_url(self, image_id):
        """Get url for an image with id 'image_id'"""
        url = "{}/image/source/{}".format(self.root, image_id)
        response = self.request(
            url, method="HEAD", allow_redirects=False, notfound="image")
        location = response.headers["location"]
        if "nicovideo.jp/login" in location:
            raise exception.StopExtraction(
                "HTTP redirect to login page (%s)", location.partition("?")[0])
        return location.replace("/o/", "/priv/", 1)

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

        raise exception.AuthorizationError(
            "username & password or 'user_session' cookie required")

    @cache(maxage=365*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        root = "https://account.nicovideo.jp"
        response = self.request(root + "/login?site=seiga")
        page = response.text

        data = {
            "mail_tel": username,
            "password": password,
        }
        url = root + text.unescape(text.extr(page, '<form action="', '"'))
        response = self.request(url, method="POST", data=data)

        if "message=cant_login" in response.url:
            raise exception.AuthenticationError()

        if "/mfa" in response.url:
            page = response.text
            email = text.extr(page, 'class="userAccount">', "<")
            code = self.input("Email Confirmation Code ({}): ".format(email))

            data = {
                "otp": code,
                "loginBtn": "Login",
                "device_name": "gdl",
            }
            url = root + text.unescape(text.extr(page, '<form action="', '"'))
            response = self.request(url, method="POST", data=data)

            if not response.history and \
                    b"Confirmation code is incorrect" in response.content:
                raise exception.AuthenticationError(
                    "Incorrect Confirmation Code")

        return {
            cookie.name: cookie.value
            for cookie in self.cookies
            if cookie.expires and cookie.domain == self.cookies_domain
        }


class SeigaUserExtractor(SeigaExtractor):
    """Extractor for images of a user from seiga.nicovideo.jp"""
    subcategory = "user"
    directory_fmt = ("{category}", "{user[id]}")
    filename_fmt = "{category}_{user[id]}_{image_id}.{extension}"
    pattern = (r"(?:https?://)?(?:www\.|(?:sp\.)?seiga\.)?nicovideo\.jp/"
               r"user/illust/(\d+)(?:\?(?:[^&]+&)*sort=([^&#]+))?")
    example = "https://seiga.nicovideo.jp/user/illust/12345"

    def __init__(self, match):
        SeigaExtractor.__init__(self, match)
        self.user_id, self.order = match.groups()
        self.start_page = 1

    def skip(self, num):
        pages, images = divmod(num, 40)
        self.start_page += pages
        self.start_image += images
        return num

    def get_metadata(self, page):
        """Collect metadata from 'page'"""
        data = text.extract_all(page, (
            ("name" , '<img alt="', '"'),
            ("msg"  , '<li class="user_message">', '</li>'),
            (None   , '<span class="target_name">すべて</span>', ''),
            ("count", '<span class="count ">', '</span>'),
        ))[0]

        if not data["name"] and "ユーザー情報が取得出来ませんでした" in page:
            raise exception.NotFoundError("user")

        return {
            "user": {
                "id": text.parse_int(self.user_id),
                "name": data["name"],
                "message": (data["msg"] or "").strip(),
            },
            "count": text.parse_int(data["count"]),
        }

    def get_images(self):
        url = "{}/user/illust/{}".format(self.root, self.user_id)
        params = {"sort": self.order, "page": self.start_page,
                  "target": "illust_all"}

        while True:
            cnt = 0
            page = self.request(url, params=params).text

            if params["page"] == self.start_page:
                yield self.get_metadata(page)

            for info in text.extract_iter(
                    page, '<li class="list_item', '</a></li> '):
                data = text.extract_all(info, (
                    ("image_id", '/seiga/im', '"'),
                    ("title"   , '<li class="title">', '</li>'),
                    ("views"   , '</span>', '</li>'),
                    ("comments", '</span>', '</li>'),
                    ("clips"   , '</span>', '</li>'),
                ))[0]
                for key in ("image_id", "views", "comments", "clips"):
                    data[key] = text.parse_int(data[key])
                yield data
                cnt += 1

            if cnt < 40:
                return
            params["page"] += 1


class SeigaImageExtractor(SeigaExtractor):
    """Extractor for single images from seiga.nicovideo.jp"""
    subcategory = "image"
    filename_fmt = "{category}_{image_id}.{extension}"
    pattern = (r"(?:https?://)?(?:"
               r"(?:seiga\.|www\.)?nicovideo\.jp/(?:seiga/im|image/source/)"
               r"|sp\.seiga\.nicovideo\.jp/seiga/#!/im"
               r"|lohas\.nicoseiga\.jp/(?:thumb|(?:priv|o)/[^/]+/\d+)/)(\d+)")
    example = "https://seiga.nicovideo.jp/seiga/im12345"

    def __init__(self, match):
        SeigaExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def skip(self, num):
        self.start_image += num
        return num

    def get_images(self):
        self.cookies.set(
            "skip_fetish_warning", "1", domain="seiga.nicovideo.jp")

        url = "{}/seiga/im{}".format(self.root, self.image_id)
        page = self.request(url, notfound="image").text

        data = text.extract_all(page, (
            ("date"        , '<li class="date"><span class="created">', '<'),
            ("title"       , '<h1 class="title">', '</h1>'),
            ("description" , '<p class="discription">', '</p>'),
        ))[0]

        data["user"] = text.extract_all(page, (
            ("id"  , '<a href="/user/illust/' , '"'),
            ("name", '<span itemprop="title">', '<'),
        ))[0]

        data["description"] = text.remove_html(data["description"])
        data["image_id"] = text.parse_int(self.image_id)
        data["date"] = text.parse_datetime(
            data["date"] + ":00+0900", "%Y年%m月%d日 %H:%M:%S%z")

        return (data, data)
