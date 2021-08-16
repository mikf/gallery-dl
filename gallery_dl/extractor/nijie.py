# -*- coding: utf-8 -*-

# Copyright 2015-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://nijie.info/"""

from .common import Extractor, Message, AsynchronousMixin
from .. import text, exception
from ..cache import cache


BASE_PATTERN = r"(?:https?://)?(?:www\.)?nijie\.info"


class NijieExtractor(AsynchronousMixin, Extractor):
    """Base class for nijie extractors"""
    category = "nijie"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{image_id}_p{num}.{extension}"
    archive_fmt = "{image_id}_{num}"
    cookiedomain = "nijie.info"
    cookienames = ("nemail", "nlogin")
    root = "https://nijie.info"
    view_url = "https://nijie.info/view.php?id="
    popup_url = "https://nijie.info/view_popup.php?id="

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.user_id = text.parse_int(match.group(1))
        self.user_name = None
        self.session.headers["Referer"] = self.root + "/"

    def items(self):
        self.login()

        for image_id in self.image_ids():

            response = self.request(self.view_url + image_id, fatal=False)
            if response.status_code >= 400:
                continue
            page = response.text

            data = self._extract_data(page)
            data["image_id"] = text.parse_int(image_id)
            yield Message.Directory, data

            for image in self._extract_images(page):
                image.update(data)
                if not image["extension"]:
                    image["extension"] = "jpg"
                yield Message.Url, image["url"], image

    def image_ids(self):
        """Collect all relevant image-ids"""

    @staticmethod
    def _extract_data(page):
        """Extract image metadata from 'page'"""
        extr = text.extract_from(page)
        keywords = text.unescape(extr(
            'name="keywords" content="', '" />')).split(",")
        data = {
            "title"      : keywords[0].strip(),
            "description": text.unescape(extr(
                '"description": "', '"').replace("&amp;", "&")),
            "date"       : text.parse_datetime(extr(
                '"datePublished": "', '"') + "+0900",
                "%a %b %d %H:%M:%S %Y%z"),
            "artist_id"  : text.parse_int(extr(
                '"sameAs": "https://nijie.info/members.php?id=', '"')),
            "artist_name": keywords[1],
            "tags"       : keywords[2:-1],
        }
        data["user_id"] = data["artist_id"]
        data["user_name"] = data["artist_name"]
        return data

    @staticmethod
    def _extract_images(page):
        """Extract image URLs from 'page'"""
        images = text.extract_iter(page, '<a href="./view_popup.php', '</a>')
        for num, image in enumerate(images):
            url = "https:" + text.extract(image, 'src="', '"')[0]
            url = url.replace("/__rs_l120x120/", "/")
            yield text.nameext_from_url(url, {
                "num": num,
                "url": url,
            })

    def login(self):
        """Login and obtain session cookies"""
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=150*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        if not username or not password:
            raise exception.AuthenticationError(
                "Username and password required")

        self.log.info("Logging in as %s", username)
        url = "{}/login_int.php".format(self.root)
        data = {"email": username, "password": password, "save": "on"}

        response = self.request(url, method="POST", data=data)
        if "//nijie.info/login.php" in response.text:
            raise exception.AuthenticationError()
        return self.session.cookies

    def _pagination(self, path):
        url = "{}/{}.php".format(self.root, path)
        params = {"id": self.user_id, "p": 1}

        while True:
            page = self.request(url, params=params, notfound="artist").text

            if not self.user_name:
                self.user_name = text.unescape(text.extract(
                    page, '<br />', '<')[0] or "")
            yield from text.extract_iter(page, 'illust_id="', '"')

            if '<a rel="next"' not in page:
                return
            params["p"] += 1


class NijieUserExtractor(NijieExtractor):
    """Extractor for nijie user profiles"""
    subcategory = "user"
    cookiedomain = None
    pattern = BASE_PATTERN + r"/members\.php\?id=(\d+)"
    test = ("https://nijie.info/members.php?id=44",)

    def items(self):
        base = "{}/{{}}.php?id={}".format(self.root, self.user_id)
        return self._dispatch_extractors((
            (NijieIllustrationExtractor, base.format("members_illust")),
            (NijieDoujinExtractor      , base.format("members_dojin")),
            (NijieFavoriteExtractor    , base.format("user_like_illust_view")),
        ), ("illustration", "doujin"))


class NijieIllustrationExtractor(NijieExtractor):
    """Extractor for all illustrations of a nijie-user"""
    subcategory = "illustration"
    pattern = BASE_PATTERN + r"/members_illust\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/members_illust.php?id=44", {
            "url": "66c4ff94c6e77c0765dd88f2d8c663055fda573e",
            "keyword": {
                "artist_id": 44,
                "artist_name": "ED",
                "date": "type:datetime",
                "description": str,
                "extension": "jpg",
                "filename": str,
                "image_id": int,
                "num": int,
                "tags": list,
                "title": str,
                "url": r"re:https://pic.nijie.net/\d+/nijie_picture/.*jpg$",
                "user_id": 44,
                "user_name": "ED",
            },
        }),
        ("https://nijie.info/members_illust.php?id=43", {
            "exception": exception.NotFoundError,
        }),
    )

    def image_ids(self):
        return self._pagination("members_illust")


class NijieDoujinExtractor(NijieExtractor):
    """Extractor for doujin entries of a nijie-user"""
    subcategory = "doujin"
    pattern = BASE_PATTERN + r"/members_dojin\.php\?id=(\d+)"
    test = ("https://nijie.info/members_dojin.php?id=6782", {
        "count": ">= 18",
        "keyword": {
            "user_id"  : 6782,
            "user_name": "ジョニー＠アビオン村",
        },
    })

    def image_ids(self):
        return self._pagination("members_dojin")


class NijieFavoriteExtractor(NijieExtractor):
    """Extractor for all favorites/bookmarks of a nijie-user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "bookmarks", "{user_id}")
    archive_fmt = "f_{user_id}_{image_id}_{num}"
    pattern = BASE_PATTERN + r"/user_like_illust_view\.php\?id=(\d+)"
    test = ("https://nijie.info/user_like_illust_view.php?id=44", {
        "count": ">= 16",
        "keyword": {
            "user_id"  : 44,
            "user_name": "ED",
        },
    })

    def image_ids(self):
        return self._pagination("user_like_illust_view")

    def _extract_data(self, page):
        data = NijieExtractor._extract_data(page)
        data["user_id"] = self.user_id
        data["user_name"] = self.user_name
        return data


class NijieImageExtractor(NijieExtractor):
    """Extractor for a work/image from nijie.info"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/view(?:_popup)?\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/view.php?id=70720", {
            "url": "5497f897311397dafa188521258624346a0af2a3",
            "keyword": "fd12bca6f4402a0c996315d28c65f7914ad70c51",
            "content": "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",
        }),
        ("https://nijie.info/view.php?id=70724", {
            "count": 0,
        }),
        ("https://nijie.info/view_popup.php?id=70720"),
    )

    def __init__(self, match):
        NijieExtractor.__init__(self, match)
        self.image_id = match.group(1)

    def image_ids(self):
        return (self.image_id,)
