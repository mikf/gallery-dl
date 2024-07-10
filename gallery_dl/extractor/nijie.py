# -*- coding: utf-8 -*-

# Copyright 2015-2023 Mike Fährmann
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
    request_interval = (2.0, 4.0)

    def __init__(self, match):
        BaseExtractor.__init__(self, match)
        self.user_id = text.parse_int(match.group(match.lastindex))

    def initialize(self):
        self.cookies_domain = "." + self.root.rpartition("/")[2]
        self.cookies_names = (self.category + "_tok",)

        BaseExtractor.initialize(self)

        self.user_name = None
        if self.category == "horne":
            self._extract_data = self._extract_data_horne

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

            urls = self._extract_images(image_id, page)
            data["count"] = len(urls)

            yield Message.Directory, data
            for num, url in enumerate(urls):
                image = text.nameext_from_url(url, {
                    "num": num,
                    "url": "https:" + url,
                })
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
        return {
            "title"      : keywords[0].strip(),
            "description": text.unescape(extr(
                '"description": "', '"').replace("&amp;", "&")),
            "date"       : text.parse_datetime(extr(
                '"datePublished": "', '"'), "%a %b %d %H:%M:%S %Y", 9),
            "artist_id"  : text.parse_int(extr('/members.php?id=', '"')),
            "artist_name": keywords[1],
            "tags"       : keywords[2:-1],
        }

    @staticmethod
    def _extract_data_horne(page):
        """Extract image metadata from 'page'"""
        extr = text.extract_from(page)
        keywords = text.unescape(extr(
            'name="keywords" content="', '" />')).split(",")
        return {
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

    def _extract_images(self, image_id, page):
        if '&#diff_1" ' in page:
            # multiple images
            url = "{}/view_popup.php?id={}".format(self.root, image_id)
            page = self.request(url).text
            return [
                text.extr(media, ' src="', '"')
                for media in text.extract_iter(
                    page, 'href="javascript:void(0);"><', '>')
            ]
        else:
            pos = page.find('id="view-center"') + 1
            # do NOT use text.extr() here, as it doesn't support a pos argument
            return (text.extract(page, 'itemprop="image" src="', '"', pos)[0],)

    @staticmethod
    def _extract_user_name(page):
        return text.unescape(text.extr(page, "<br />", "<"))

    def login(self):
        if self.cookies_check(self.cookies_names):
            return

        username, password = self._get_auth_info()
        if username:
            return self.cookies_update(self._login_impl(username, password))

        raise exception.AuthenticationError("Username and password required")

    @cache(maxage=90*86400, keyarg=1)
    def _login_impl(self, username, password):
        self.log.info("Logging in as %s", username)

        url = "{}/login_int.php".format(self.root)
        data = {"email": username, "password": password, "save": "on"}

        response = self.request(url, method="POST", data=data)
        if "/login.php" in response.text:
            raise exception.AuthenticationError()
        return self.cookies

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
    cookies_domain = None
    pattern = BASE_PATTERN + r"/members\.php\?id=(\d+)"
    example = "https://nijie.info/members.php?id=12345"

    def initialize(self):
        pass

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
    example = "https://nijie.info/members_illust.php?id=12345"

    def image_ids(self):
        return self._pagination("members_illust")


class NijieDoujinExtractor(NijieExtractor):
    """Extractor for doujin entries of a nijie user"""
    subcategory = "doujin"
    pattern = BASE_PATTERN + r"/members_dojin\.php\?id=(\d+)"
    example = "https://nijie.info/members_dojin.php?id=12345"

    def image_ids(self):
        return self._pagination("members_dojin")


class NijieFavoriteExtractor(NijieExtractor):
    """Extractor for all favorites/bookmarks of a nijie user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "bookmarks", "{user_id}")
    archive_fmt = "f_{user_id}_{image_id}_{num}"
    pattern = BASE_PATTERN + r"/user_like_illust_view\.php\?id=(\d+)"
    example = "https://nijie.info/user_like_illust_view.php?id=12345"

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
    example = "https://nijie.info/history_nuita.php?id=12345"

    def image_ids(self):
        return self._pagination("history_nuita")

    def _extract_data(self, page):
        data = NijieExtractor._extract_data(page)
        data["user_id"] = self.user_id
        data["user_name"] = self.user_name
        return data

    @staticmethod
    def _extract_user_name(page):
        return text.unescape(text.extr(page, "<title>", "さんの抜いた"))


class NijieFeedExtractor(NijieExtractor):
    """Extractor for nijie liked user feed"""
    subcategory = "feed"
    pattern = BASE_PATTERN + r"/like_user_view\.php"
    example = "https://nijie.info/like_user_view.php"

    def image_ids(self):
        return self._pagination("like_user_view")

    @staticmethod
    def _extract_user_name(page):
        return ""


class NijieFollowedExtractor(NijieExtractor):
    """Extractor for followed nijie users"""
    subcategory = "followed"
    pattern = BASE_PATTERN + r"/like_my\.php"
    example = "https://nijie.info/like_my.php"

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
    example = "https://nijie.info/view.php?id=12345"

    def __init__(self, match):
        NijieExtractor.__init__(self, match)
        self.image_id = match.group(match.lastindex)

    def image_ids(self):
        return (self.image_id,)
