# -*- coding: utf-8 -*-

# Copyright 2015-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for nijie instances"""

from .common import BaseExtractor, Message, AsynchronousMixin
from .. import text, exception
from ..cache import cache


class NijieExtractor(AsynchronousMixin, BaseExtractor):
    """Base class for nijie extractors"""
    basecategory = "Nijie"
    directory_fmt = ("{category}", "{user_id}")
    filename_fmt = "{image_id}_p{num}.{extension}"
    archive_fmt = "{image_id}_{num}"

    def __init__(self, match):
        self._init_category(match)
        self.cookiedomain = "." + self.root.rpartition("/")[2]
        self.cookienames = (self.category + "_tok",)

        if self.category == "horne":
            self._extract_data = self._extract_data_horne

        BaseExtractor.__init__(self, match)

        self.user_id = text.parse_int(match.group(match.lastindex))
        self.user_name = None
        self.session.headers["Referer"] = self.root + "/"

    def items(self):
        self.login()

        for image_id in self.image_ids():

            url = "{}/view.php?id={}".format(self.root, image_id)
            response = self.request(url, fatal=False)
            if response.status_code >= 400:
                continue
            page = response.text

            data = self._extract_data(page)
            data["image_id"] = text.parse_int(image_id)

            if self.user_name:
                data["user_id"] = self.user_id
                data["user_name"] = self.user_name
            else:
                data["user_id"] = data["artist_id"]
                data["user_name"] = data["artist_name"]
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
                '"datePublished": "', '"'), "%a %b %d %H:%M:%S %Y", 9),
            "artist_id"  : text.parse_int(extr('/members.php?id=', '"')),
            "artist_name": keywords[1],
            "tags"       : keywords[2:-1],
        }
        return data

    @staticmethod
    def _extract_data_horne(page):
        """Extract image metadata from 'page'"""
        extr = text.extract_from(page)
        keywords = text.unescape(extr(
            'name="keywords" content="', '" />')).split(",")
        data = {
            "title"      : keywords[0].strip(),
            "description": text.unescape(extr(
                'property="og:description" content="', '"')),
            "artist_id"  : text.parse_int(extr('members.php?id=', '"')),
            "artist_name": keywords[1],
            "tags"       : keywords[2:-1],
            "date"       : text.parse_datetime(extr(
                "itemprop='datePublished' content=", "<").rpartition(">")[2],
                "%Y-%m-%d %H:%M:%S", 9),
        }
        return data

    @staticmethod
    def _extract_images(page):
        """Extract image URLs from 'page'"""
        images = text.extract_iter(page, "/view_popup.php", "</a>")
        for num, image in enumerate(images):
            src = text.extract(image, 'src="', '"')[0]
            if not src:
                continue
            url = ("https:" + src).replace("/__rs_l120x120/", "/")
            yield text.nameext_from_url(url, {
                "num": num,
                "url": url,
            })

    @staticmethod
    def _extract_user_name(page):
        return text.unescape(text.extract(page, "<br />", "<")[0] or "")

    def login(self):
        """Login and obtain session cookies"""
        if not self._check_cookies(self.cookienames):
            username, password = self._get_auth_info()
            self._update_cookies(self._login_impl(username, password))

    @cache(maxage=90*24*3600, keyarg=1)
    def _login_impl(self, username, password):
        if not username or not password:
            raise exception.AuthenticationError(
                "Username and password required")

        self.log.info("Logging in as %s", username)
        url = "{}/login_int.php".format(self.root)
        data = {"email": username, "password": password, "save": "on"}

        response = self.request(url, method="POST", data=data)
        if "/login.php" in response.text:
            raise exception.AuthenticationError()
        return self.session.cookies

    def _pagination(self, path):
        url = "{}/{}.php".format(self.root, path)
        params = {"id": self.user_id, "p": 1}

        while True:
            page = self.request(url, params=params, notfound="artist").text

            if self.user_name is None:
                self.user_name = self._extract_user_name(page)
            yield from text.extract_iter(page, 'illust_id="', '"')

            if '<a rel="next"' not in page:
                return
            params["p"] += 1


BASE_PATTERN = NijieExtractor.update({
    "nijie": {
        "root": "https://nijie.info",
        "pattern": r"(?:www\.)?nijie\.info",
    },
    "horne": {
        "root": "https://horne.red",
        "pattern": r"(?:www\.)?horne\.red",
    },
})


class NijieUserExtractor(NijieExtractor):
    """Extractor for nijie user profiles"""
    subcategory = "user"
    cookiedomain = None
    pattern = BASE_PATTERN + r"/members\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/members.php?id=44"),
        ("https://horne.red/members.php?id=58000"),
    )

    def items(self):
        fmt = "{}/{{}}.php?id={}".format(self.root, self.user_id).format
        return self._dispatch_extractors((
            (NijieIllustrationExtractor, fmt("members_illust")),
            (NijieDoujinExtractor      , fmt("members_dojin")),
            (NijieFavoriteExtractor    , fmt("user_like_illust_view")),
            (NijieNuitaExtractor       , fmt("history_nuita")),
        ), ("illustration", "doujin"))


class NijieIllustrationExtractor(NijieExtractor):
    """Extractor for all illustrations of a nijie-user"""
    subcategory = "illustration"
    pattern = BASE_PATTERN + r"/members_illust\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/members_illust.php?id=44", {
            "url": "1553e5144df50a676f5947d02469299b401ad6c0",
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
                "url": r"re:https://pic.nijie.net/\d+/nijie/.*jpg$",
                "user_id": 44,
                "user_name": "ED",
            },
        }),
        ("https://horne.red/members_illust.php?id=58000", {
            "pattern": r"https://pic\.nijie\.net/\d+/horne/\d+/\d+/\d+"
                       r"/illust/\d+_\d+_[0-9a-f]+_[0-9a-f]+\.png",
            "range": "1-20",
            "count": 20,
            "keyword": {
                "artist_id": 58000,
                "artist_name": "のえるわ",
                "date": "type:datetime",
                "description": str,
                "image_id": int,
                "num": int,
                "tags": list,
                "title": str,
                "url": str,
                "user_id": 58000,
                "user_name": "のえるわ",
            },
        }),
        ("https://nijie.info/members_illust.php?id=43", {
            "exception": exception.NotFoundError,
        }),
    )

    def image_ids(self):
        return self._pagination("members_illust")


class NijieDoujinExtractor(NijieExtractor):
    """Extractor for doujin entries of a nijie user"""
    subcategory = "doujin"
    pattern = BASE_PATTERN + r"/members_dojin\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/members_dojin.php?id=6782", {
            "count": ">= 18",
            "keyword": {
                "user_id"  : 6782,
                "user_name": "ジョニー＠アビオン村",
            },
        }),
        ("https://horne.red/members_dojin.php?id=58000"),
    )

    def image_ids(self):
        return self._pagination("members_dojin")


class NijieFavoriteExtractor(NijieExtractor):
    """Extractor for all favorites/bookmarks of a nijie user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "bookmarks", "{user_id}")
    archive_fmt = "f_{user_id}_{image_id}_{num}"
    pattern = BASE_PATTERN + r"/user_like_illust_view\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/user_like_illust_view.php?id=44", {
            "count": ">= 16",
            "keyword": {
                "user_id"  : 44,
                "user_name": "ED",
            },
        }),
        ("https://horne.red/user_like_illust_view.php?id=58000", {
            "range": "1-5",
            "count": 5,
            "keyword": {
                "user_id"  : 58000,
                "user_name": "のえるわ",
            },
        }),
    )

    def image_ids(self):
        return self._pagination("user_like_illust_view")

    def _extract_data(self, page):
        data = NijieExtractor._extract_data(page)
        data["user_id"] = self.user_id
        data["user_name"] = self.user_name
        return data


class NijieNuitaExtractor(NijieExtractor):
    """Extractor for a nijie user's 抜いた list"""
    subcategory = "nuita"
    directory_fmt = ("{category}", "nuita", "{user_id}")
    archive_fmt = "n_{user_id}_{image_id}_{num}"
    pattern = BASE_PATTERN + r"/history_nuita\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/history_nuita.php?id=728995", {
            "range": "1-10",
            "count": 10,
            "keyword": {
                "user_id"  : 728995,
                "user_name": "莚",
            },
        }),
        ("https://horne.red/history_nuita.php?id=58000"),
    )

    def image_ids(self):
        return self._pagination("history_nuita")

    def _extract_data(self, page):
        data = NijieExtractor._extract_data(page)
        data["user_id"] = self.user_id
        data["user_name"] = self.user_name
        return data

    @staticmethod
    def _extract_user_name(page):
        return text.unescape(text.extract(
            page, "<title>", "さんの抜いた")[0] or "")


class NijieFeedExtractor(NijieExtractor):
    """Extractor for nijie liked user feed"""
    subcategory = "feed"
    pattern = BASE_PATTERN + r"/like_user_view\.php"
    test = (
        ("https://nijie.info/like_user_view.php", {
            "range": "1-10",
            "count": 10,
        }),
        ("https://horne.red/like_user_view.php"),
    )

    def image_ids(self):
        return self._pagination("like_user_view")

    @staticmethod
    def _extract_user_name(page):
        return ""


class NijiefollowedExtractor(NijieExtractor):
    """Extractor for followed nijie users"""
    subcategory = "followed"
    pattern = BASE_PATTERN + r"/like_my\.php"
    test = (
        ("https://nijie.info/like_my.php"),
        ("https://horne.red/like_my.php"),
    )

    def items(self):
        self.login()

        url = self.root + "/like_my.php"
        params = {"p": 1}
        data = {"_extractor": NijieUserExtractor}

        while True:
            page = self.request(url, params=params).text

            for user_id in text.extract_iter(
                    page, '"><a href="/members.php?id=', '"'):
                user_url = "{}/members.php?id={}".format(self.root, user_id)
                yield Message.Queue, user_url, data

            if '<a rel="next"' not in page:
                return
            params["p"] += 1


class NijieImageExtractor(NijieExtractor):
    """Extractor for a nijie work/image"""
    subcategory = "image"
    pattern = BASE_PATTERN + r"/view(?:_popup)?\.php\?id=(\d+)"
    test = (
        ("https://nijie.info/view.php?id=70720", {
            "url": "3d654e890212ba823c9647754767336aebc0a743",
            "keyword": "41da5d0e178b04f01fe72460185df52fadc3c91b",
            "content": "d85e3ea896ed5e4da0bca2390ad310a4df716ca6",
        }),
        ("https://nijie.info/view.php?id=70724", {
            "count": 0,
        }),
        ("https://nijie.info/view_popup.php?id=70720"),
        ("https://horne.red/view.php?id=8716", {
            "count": 4,
            "keyword": {
                "artist_id": 58000,
                "artist_name": "のえるわ",
                "date": "dt:2018-02-04 14:47:24",
                "description": "ノエル「そんなことしなくても、"
                               "言ってくれたら咥えるのに・・・♡」",
                "image_id": 8716,
                "tags": ["男の娘", "フェラ", "オリキャラ", "うちのこ"],
                "title": "ノエル「いまどきそんな、恵方巻ネタなんてやらなくても・・・」",
                "user_id": 58000,
                "user_name": "のえるわ",
            },
        }),
    )

    def __init__(self, match):
        NijieExtractor.__init__(self, match)
        self.image_id = match.group(match.lastindex)

    def image_ids(self):
        return (self.image_id,)
