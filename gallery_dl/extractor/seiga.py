# -*- coding: utf-8 -*-

# Copyright 2016-2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://seiga.nicovideo.jp/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache


class SeigaExtractor(Extractor):
    """Base class for seiga extractors"""
    category = "seiga"
    archive_fmt = "{image_id}"
    cookiedomain = ".nicovideo.jp"
    root = "https://seiga.nicovideo.jp"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.start_image = 0

    def items(self):
        self.login()
        images = iter(self.get_images())
        data = next(images)

        yield Message.Version, 1
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
        return response.headers["Location"].replace("/o/", "/priv/", 1)

    def login(self):
        """Login and set necessary cookies"""
        if not self._check_cookies(("user_session",)):
            username, password = self._get_auth_info()
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=7*24*3600, keyarg=1)
    def _login_impl(self, username, password):
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
    directory_fmt = ("{category}", "{user[id]}")
    filename_fmt = "{category}_{user[id]}_{image_id}.{extension}"
    pattern = (r"(?:https?://)?(?:www\.|(?:sp\.)?seiga\.)?nicovideo\.jp/"
               r"user/illust/(\d+)(?:\?(?:[^&]+&)*sort=([^&#]+))?")
    test = (
        ("https://seiga.nicovideo.jp/user/illust/39537793", {
            "pattern": r"https://lohas\.nicoseiga\.jp/priv/[0-9a-f]+/\d+/\d+",
            "count": ">= 4",
            "keyword": {
                "user": {
                    "id": 39537793,
                    "message": str,
                    "name": str,
                },
                "clips": int,
                "comments": int,
                "count": int,
                "extension": None,
                "image_id": int,
                "title": str,
                "views": int,
            },
        }),
        ("https://seiga.nicovideo.jp/user/illust/79433", {
            "exception": exception.NotFoundError,
        }),
        ("https://seiga.nicovideo.jp/user/illust/39537793"
         "?sort=image_view&target=illust_all"),
        ("https://sp.seiga.nicovideo.jp/user/illust/39537793"),
    )

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
    test = (
        ("https://seiga.nicovideo.jp/seiga/im5977527", {
            "keyword": "f66ba5de33d4ce2cb57f23bb37e1e847e0771c10",
            "content": "d9202292012178374d57fb0126f6124387265297",
        }),
        ("https://seiga.nicovideo.jp/seiga/im123", {
            "exception": exception.NotFoundError,
        }),
        ("https://seiga.nicovideo.jp/image/source/5977527"),
        ("https://sp.seiga.nicovideo.jp/seiga/#!/im5977527"),
        ("https://lohas.nicoseiga.jp/thumb/5977527i"),
        ("https://lohas.nicoseiga.jp/priv"
         "/759a4ef1c639106ba4d665ee6333832e647d0e4e/1549727594/5977527"),
        ("https://lohas.nicoseiga.jp/o"
         "/759a4ef1c639106ba4d665ee6333832e647d0e4e/1549727594/5977527"),
    )

    def __init__(self, match):
        SeigaExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def skip(self, num):
        self.start_image += num
        return num

    def get_images(self):
        return ({}, {"image_id": text.parse_int(self.image_id)})
