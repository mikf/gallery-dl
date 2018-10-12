# -*- coding: utf-8 -*-

# Copyright 2014-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and ugoira from https://www.pixiv.net/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
from datetime import datetime, timedelta


class PixivExtractor(Extractor):
    """Base class for pixiv extractors"""
    category = "pixiv"
    directory_fmt = ["{category}", "{user[id]} {user[account]}"]
    filename_fmt = "{category}_{user[id]}_{id}{num}.{extension}"
    archive_fmt = "{id}{num}.{extension}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = PixivAppAPI(self)
        self.user_id = -1
        self.load_ugoira = self.config("ugoira", True)

    def items(self):
        metadata = self.get_metadata()

        yield Message.Version, 1
        yield Message.Directory, metadata

        for work in self.works():
            if not work["user"]["id"]:
                continue

            meta_single_page = work["meta_single_page"]
            meta_pages = work["meta_pages"]
            del work["meta_single_page"]
            del work["image_urls"]
            del work["meta_pages"]
            work["num"] = ""
            work["tags"] = [tag["name"] for tag in work["tags"]]
            work.update(metadata)

            if work["type"] == "ugoira":
                if not self.load_ugoira:
                    continue
                ugoira = self.api.ugoira_metadata(work["id"])

                url = ugoira["zip_urls"]["medium"].replace(
                    "_ugoira600x600", "_ugoira1920x1080")
                work["frames"] = ugoira["frames"]
                work["extension"] = "zip"
                yield Message.Url, url, work

            elif work["page_count"] == 1:
                url = meta_single_page["original_image_url"]
                work["extension"] = url.rpartition(".")[2]
                yield Message.Url, url, work

            else:
                for num, img in enumerate(meta_pages):
                    url = img["image_urls"]["original"]
                    work["num"] = "_p{:02}".format(num)
                    work["extension"] = url.rpartition(".")[2]
                    yield Message.Url, url, work

    def works(self):
        """Return an iterable containing all relevant 'work'-objects"""

    def get_metadata(self, user=None):
        """Collect metadata for extractor-job"""
        if not user:
            user = self.api.user_detail(self.user_id)
        return {"user": user}


class PixivUserExtractor(PixivExtractor):
    """Extractor for works of a pixiv-user"""
    subcategory = "user"
    pattern = [(r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
                r"/member(?:_illust)?\.php\?id=(\d+)(?:&([^#]+))?"),
               (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
                r"/(?:u(?:ser)?/|(?:mypage\.php)?#id=)(\d+)()")]
    test = [
        ("http://www.pixiv.net/member_illust.php?id=173530", {
            "url": "852c31ad83b6840bacbce824d85f2a997889efb7",
        }),
        # illusts with specific tag
        (("https://www.pixiv.net/member_illust.php?id=173530"
          "&tag=%E6%89%8B%E3%81%B6%E3%82%8D"), {
            "url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
        }),
        ("http://www.pixiv.net/member_illust.php?id=173531", {
            "exception": exception.NotFoundError,
        }),
        ("https://www.pixiv.net/u/173530", None),
        ("https://www.pixiv.net/user/173530", None),
        ("https://www.pixiv.net/mypage.php#id=173530", None),
        ("https://www.pixiv.net/#id=173530", None),
        ("https://touch.pixiv.net/member_illust.php?id=173530", None),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.user_id = match.group(1)
        self.query = text.parse_query(match.group(2))

    def works(self):
        works = self.api.user_illusts(self.user_id)

        if "tag" in self.query:
            tag = text.unquote(self.query["tag"]).lower()
            works = (
                work for work in works
                if tag in [t["name"].lower() for t in work["tags"]]
            )

        return works


class PixivMeExtractor(PixivExtractor):
    """Extractor for pixiv.me URLs"""
    subcategory = "me"
    pattern = [r"(?:https?://)?pixiv\.me/([^/?&#]+)"]
    test = [
        ("https://pixiv.me/del_shannon", {
            "url": "0b1a18c3e3553c44ee6e0ccc36a7fd906c498e8f",
        }),
        ("https://pixiv.me/del_shanno", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.account = match.group(1)

    def items(self):
        url = "https://pixiv.me/" + self.account
        response = self.request(
            url, method="HEAD", allow_redirects=False, expect=(404,))
        if response.status_code == 404:
            raise exception.NotFoundError("user")
        yield Message.Version, 1
        yield Message.Queue, response.headers["Location"], {}


class PixivWorkExtractor(PixivExtractor):
    """Extractor for a single pixiv work/illustration"""
    subcategory = "work"
    pattern = [(r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
                r"/member(?:_illust)?\.php\?(?:[^&]+&)*illust_id=(\d+)"),
               (r"(?:https?://)?i(?:\d+\.pixiv|\.pximg)\.net"
                r"/(?:(?:.*/)?img-[^/]+/img/\d{4}(?:/\d\d){5}"
                r"|img\d+/img/[^/]+)/(\d+)"),
               (r"(?:https?://)?img\d*\.pixiv\.net/img/[^/]+/(\d+)"),
               (r"(?:https?://)?(?:www\.)?pixiv\.net/i/(\d+)")]
    test = [
        (("http://www.pixiv.net/member_illust.php"
          "?mode=medium&illust_id=966412"), {
            "url": "90c1715b07b0d1aad300bce256a0bc71f42540ba",
            "content": "69a8edfb717400d1c2e146ab2b30d2c235440c5a",
        }),
        (("http://www.pixiv.net/member_illust.php"
          "?mode=medium&illust_id=966411"), {
            "exception": exception.NotFoundError,
        }),
        # ugoira
        (("https://www.pixiv.net/member_illust.php"
          "?mode=medium&illust_id=66806629"), {
            "url": "7267695a985c4db8759bebcf8d21dbdd2d2317ef",
            "keywords": {"frames": list},
        }),
        (("http://i1.pixiv.net/c/600x600/img-master/"
          "img/2008/06/13/00/29/13/966412_p0_master1200.jpg"), None),
        (("https://i.pximg.net/img-original/"
          "img/2017/04/25/07/33/29/62568267_p0.png"), None),
        ("https://www.pixiv.net/i/966412", None),
        ("http://img.pixiv.net/img/soundcross/42626136.jpg", None),
        ("http://i2.pixiv.net/img76/img/snailrin/42672235.jpg", None),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.illust_id = match.group(1)
        self.load_ugoira = True
        self.work = None

    def works(self):
        return (self.work,)

    def get_metadata(self, user=None):
        self.work = self.api.illust_detail(self.illust_id)
        return PixivExtractor.get_metadata(self, self.work["user"])


class PixivFavoriteExtractor(PixivExtractor):
    """Extractor for all favorites/bookmarks of a pixiv-user"""
    subcategory = "favorite"
    directory_fmt = ["{category}", "bookmarks",
                     "{user_bookmark[id]} {user_bookmark[account]}"]
    archive_fmt = "f_{user_bookmark[id]}_{id}{num}.{extension}"
    pattern = [r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/bookmark\.php(?:\?([^#]*))?"]
    test = [
        ("https://www.pixiv.net/bookmark.php?id=173530", {
            "url": "e717eb511500f2fa3497aaee796a468ecf685cc4",
        }),
        # bookmarks with specific tag
        (("https://www.pixiv.net/bookmark.php?id=3137110"
          "&tag=%E3%81%AF%E3%82%93%E3%82%82%E3%82%93&p=1"), {
            "count": 2,
        }),
        # own bookmarks
        ("https://www.pixiv.net/bookmark.php", {
            "url": "90c1715b07b0d1aad300bce256a0bc71f42540ba",
        }),
        # touch URLs
        ("https://touch.pixiv.net/bookmark.php?id=173530", None),
        ("https://touch.pixiv.net/bookmark.php", None),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.query = text.parse_query(match.group(1))
        if "id" not in self.query:
            self.subcategory = "bookmark"

    def works(self):
        tag = None
        restrict = "public"

        if "tag" in self.query:
            tag = text.unquote(self.query["tag"])
        if "rest" in self.query and self.query["rest"] == "hide":
            restrict = "private"

        return self.api.user_bookmarks_illust(self.user_id, tag, restrict)

    def get_metadata(self, user=None):
        if "id" in self.query:
            user = self.api.user_detail(self.query["id"])
        else:
            self.api.login()
            user = self.api.user

        self.user_id = user["id"]
        return {"user_bookmark": user}


class PixivRankingExtractor(PixivExtractor):
    """Extractor for pixiv ranking pages"""
    subcategory = "ranking"
    archive_fmt = "r_{ranking[mode]}_{ranking[date]}_{id}{num}.{extension}"
    directory_fmt = ["{category}", "rankings",
                     "{ranking[mode]}", "{ranking[date]}"]
    pattern = [r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/ranking\.php(?:\?([^#]*))?"]
    test = [
        ("https://www.pixiv.net/ranking.php?mode=daily&date=20170818", None),
        ("https://www.pixiv.net/ranking.php", None),
        ("https://touch.pixiv.net/ranking.php", None),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.query = match.group(1)
        self.mode = self.date = None

    def works(self):
        return self.api.illust_ranking(self.mode, self.date)

    def get_metadata(self, user=None):
        query = text.parse_query(self.query)

        mode = query.get("mode", "daily").lower()
        mode_map = {
            "daily": "day",
            "daily_r18": "day_r18",
            "weekly": "week",
            "weekly_r18": "week_r18",
            "monthly": "month",
            "male": "day_male",
            "male_r18": "day_male_r18",
            "female": "day_female",
            "female_r18": "day_female_r18",
            "original": "week_original",
            "rookie": "week_rookie",
            "r18g": "week_r18g",
        }
        if mode not in mode_map:
            self.log.warning("invalid mode '%s'", mode)
            mode = "daily"
        self.mode = mode_map[mode]

        date = query.get("date")
        if date:
            if len(date) == 8 and date.isdecimal():
                date = "{}-{}-{}".format(date[0:4], date[4:6], date[6:8])
            else:
                self.log.warning("invalid date '%s'", date)
                date = None
        if not date:
            date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.date = date

        return {"ranking": {
            "mode": mode,
            "date": self.date,
        }}


class PixivSearchExtractor(PixivExtractor):
    """Extractor for pixiv search results"""
    subcategory = "search"
    archive_fmt = "s_{search[word]}_{id}{num}.{extension}"
    directory_fmt = ["{category}", "search", "{search[word]}"]
    pattern = [r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/search\.php\?([^#]+)"]
    test = [
        ("https://www.pixiv.net/search.php?s_mode=s_tag&word=Original", None),
        ("https://touch.pixiv.net/search.php?word=Original", None),
    ]

    def __init__(self, match):
        PixivExtractor.__init__(self)
        self.query = match.group(1)
        self.word = self.sort = self.target = None

    def works(self):
        return self.api.search_illust(self.word, self.sort, self.target)

    def get_metadata(self, user=None):
        query = text.parse_query(self.query)

        if "word" in query:
            self.word = text.unescape(query["word"])
        else:
            self.log.error("missing search term")
            raise exception.StopExtraction()

        sort = query.get("order", "date_d")
        sort_map = {
            "date": "date_asc",
            "date_d": "date_desc",
        }
        if sort not in sort_map:
            self.log.warning("invalid sort order '%s'", sort)
            sort = "date_d"
        self.sort = sort_map[sort]

        target = query.get("s_mode", "s_tag")
        target_map = {
            "s_tag": "partial_match_for_tags",
            "s_tag_full": "exact_match_for_tags",
            "s_tc": "title_and_caption",
        }
        if target not in target_map:
            self.log.warning("invalid search target '%s'", target)
            target = "s_tag"
        self.target = target_map[target]

        return {"search": {
            "word": self.word,
            "sort": self.sort,
            "target": self.target,
        }}


class PixivFollowExtractor(PixivExtractor):
    """Extractor for new illustrations from your followed artists"""
    subcategory = "follow"
    archive_fmt = "F_{user_follow[id]}_{id}{num}.{extension}"
    directory_fmt = ["{category}", "following"]
    pattern = [r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/bookmark_new_illust\.php"]
    test = [
        ("https://www.pixiv.net/bookmark_new_illust.php", None),
        ("https://touch.pixiv.net/bookmark_new_illust.php", None),
    ]

    def __init__(self, _):
        PixivExtractor.__init__(self)

    def works(self):
        return self.api.illust_follow()

    def get_metadata(self, user=None):
        self.api.login()
        return {"user_follow": self.api.user}


class PixivAppAPI():
    """Minimal interface for the Pixiv App API for mobile devices

    For a more complete implementation or documentation, see
    - https://github.com/upbit/pixivpy
    - https://gist.github.com/ZipFile/3ba99b47162c23f8aea5d5942bb557b1
    """
    CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
    CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"

    def __init__(self, extractor):
        self.session = extractor.session
        self.log = extractor.log
        self.username, self.password = extractor._get_auth_info()
        self.user = None

        self.client_id = extractor.config(
            "client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

        self.session.headers.update({
            "App-OS": "ios",
            "App-OS-Version": "10.3.1",
            "App-Version": "6.7.1",
            "User-Agent": "PixivIOSApp/6.7.1 (iOS 10.3.1; iPhone8,1)",
            "Referer": "https://app-api.pixiv.net/",
        })

    def login(self):
        """Login and gain an access token"""
        self.user, auth = self._login_impl(
            self.username, self.password)
        self.session.headers["Authorization"] = auth

    @cache(maxage=3590, keyarg=1)
    def _login_impl(self, username, password):
        url = "https://oauth.secure.pixiv.net/auth/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "get_secure_url": 1,
        }
        refresh_token = _refresh_token_cache(username)

        if refresh_token:
            self.log.info("Refreshing access token")
            data["grant_type"] = "refresh_token"
            data["refresh_token"] = refresh_token
        else:
            self.log.info("Logging in as %s", username)
            data["grant_type"] = "password"
            data["username"] = username
            data["password"] = password

        response = self.session.post(url, data=data)
        if response.status_code >= 400:
            raise exception.AuthenticationError()

        data = response.json()["response"]
        if not refresh_token:
            _refresh_token_cache.update(username, data["refresh_token"])
        return data["user"], "Bearer " + data["access_token"]

    def illust_detail(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("v1/illust/detail", params)["illust"]

    def illust_follow(self, restrict="all"):
        params = {"restrict": restrict}
        return self._pagination("v2/illust/follow", params)

    def illust_ranking(self, mode="day", date=None):
        params = {"mode": mode, "date": date}
        return self._pagination("v1/illust/ranking", params)

    def search_illust(self, word, sort=None, target=None, duration=None):
        params = {"word": word, "search_target": target,
                  "sort": sort, "duration": duration}
        return self._pagination("v1/search/illust", params)

    def user_bookmarks_illust(self, user_id, tag=None, restrict="public"):
        params = {"user_id": user_id, "tag": tag, "restrict": restrict}
        return self._pagination("v1/user/bookmarks/illust", params)

    def user_detail(self, user_id):
        params = {"user_id": user_id}
        return self._call("v1/user/detail", params)["user"]

    def user_illusts(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("v1/user/illusts", params)

    def ugoira_metadata(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("v1/ugoira/metadata", params)["ugoira_metadata"]

    def _call(self, endpoint, params=None):
        url = "https://app-api.pixiv.net/" + endpoint

        self.login()
        response = self.session.get(url, params=params)

        if 200 <= response.status_code < 400:
            return response.json()
        if response.status_code == 404:
            raise exception.NotFoundError()
        self.log.error("API request failed: %s", response.text)
        raise exception.StopExtraction()

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            yield from data["illusts"]

            if not data["next_url"]:
                return
            query = data["next_url"].rpartition("?")[2]
            params = text.parse_query(query)


@cache(maxage=365*24*60*60, keyarg=0)
def _refresh_token_cache(username):
    return None
