# -*- coding: utf-8 -*-

# Copyright 2014-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images and ugoira from https://www.pixiv.net/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import cache
from datetime import datetime, timedelta
import itertools
import hashlib
import time


class PixivExtractor(Extractor):
    """Base class for pixiv extractors"""
    category = "pixiv"
    directory_fmt = ("{category}", "{user[id]} {user[account]}")
    filename_fmt = "{id}_p{num}.{extension}"
    archive_fmt = "{id}{suffix}.{extension}"
    cookiedomain = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.api = PixivAppAPI(self)
        self.load_ugoira = self.config("ugoira", True)
        self.translated_tags = self.config("translated-tags", False)

    def items(self):
        tkey = "translated_name" if self.translated_tags else "name"
        ratings = {0: "General", 1: "R-18", 2: "R-18G"}
        metadata = self.metadata()

        for work in self.works():
            if not work["user"]["id"]:
                continue

            meta_single_page = work["meta_single_page"]
            meta_pages = work["meta_pages"]
            del work["meta_single_page"]
            del work["image_urls"]
            del work["meta_pages"]
            work["num"] = 0
            work["tags"] = [tag[tkey] or tag["name"] for tag in work["tags"]]
            work["date"] = text.parse_datetime(work["create_date"])
            work["rating"] = ratings.get(work["x_restrict"])
            work["suffix"] = ""
            work.update(metadata)

            yield Message.Directory, work

            if work["type"] == "ugoira":
                if not self.load_ugoira:
                    continue
                ugoira = self.api.ugoira_metadata(work["id"])

                url = ugoira["zip_urls"]["medium"].replace(
                    "_ugoira600x600", "_ugoira1920x1080")
                work["frames"] = ugoira["frames"]
                yield Message.Url, url, text.nameext_from_url(url, work)

            elif work["page_count"] == 1:
                url = meta_single_page["original_image_url"]
                yield Message.Url, url, text.nameext_from_url(url, work)

            else:
                for work["num"], img in enumerate(meta_pages):
                    url = img["image_urls"]["original"]
                    work["suffix"] = "_p{:02}".format(work["num"])
                    yield Message.Url, url, text.nameext_from_url(url, work)

    def works(self):
        """Return an iterable containing all relevant 'work'-objects"""

    def metadata(self):
        """Collect metadata for extractor-job"""
        return {}


class PixivUserExtractor(PixivExtractor):
    """Extractor for works of a pixiv-user"""
    subcategory = "user"
    pattern = (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net/(?:"
               r"(?:en/)?users/(\d+)(?:/(?:artworks|illustrations|manga)"
               r"(?:/([^/?#]+))?)?/?(?:$|[?#])"
               r"|member(?:_illust)?\.php\?id=(\d+)(?:&([^#]+))?"
               r"|(?:u(?:ser)?/|(?:mypage\.php)?#id=)(\d+))")
    test = (
        ("https://www.pixiv.net/en/users/173530/artworks", {
            "url": "852c31ad83b6840bacbce824d85f2a997889efb7",
        }),
        # illusts with specific tag
        (("https://www.pixiv.net/en/users/173530/artworks"
          "/%E6%89%8B%E3%81%B6%E3%82%8D"), {
            "url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
        }),
        (("https://www.pixiv.net/member_illust.php?id=173530"
          "&tag=%E6%89%8B%E3%81%B6%E3%82%8D"), {
            "url": "25b1cd81153a8ff82eec440dd9f20a4a22079658",
        }),
        # avatar (#595, 623)
        ("https://www.pixiv.net/en/users/173530", {
            "options": (("avatar", True),),
            "content": "4e57544480cc2036ea9608103e8f024fa737fe66",
            "range": "1",
        }),
        # deleted account
        ("http://www.pixiv.net/member_illust.php?id=173531", {
            "count": 0,
        }),
        ("https://www.pixiv.net/en/users/173530"),
        ("https://www.pixiv.net/en/users/173530/manga"),
        ("https://www.pixiv.net/en/users/173530/illustrations"),
        ("https://www.pixiv.net/member_illust.php?id=173530"),
        ("https://www.pixiv.net/u/173530"),
        ("https://www.pixiv.net/user/173530"),
        ("https://www.pixiv.net/mypage.php#id=173530"),
        ("https://www.pixiv.net/#id=173530"),
        ("https://touch.pixiv.net/member_illust.php?id=173530"),
    )

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        u1, t1, u2, t2, u3 = match.groups()
        if t1:
            t1 = text.unquote(t1)
        elif t2:
            t2 = text.parse_query(t2).get("tag")
        self.user_id = u1 or u2 or u3
        self.tag = t1 or t2

    def works(self):
        works = self.api.user_illusts(self.user_id)

        if self.tag:
            tag = self.tag.lower()
            works = (
                work for work in works
                if tag in [t["name"].lower() for t in work["tags"]]
            )

        if self.config("avatar"):
            user = self.api.user_detail(self.user_id)
            url = user["profile_image_urls"]["medium"].replace("_170.", ".")
            avatar = {
                "create_date"     : None,
                "height"          : 0,
                "id"              : "avatar",
                "image_urls"      : None,
                "meta_pages"      : (),
                "meta_single_page": {"original_image_url": url},
                "page_count"      : 1,
                "sanity_level"    : 0,
                "tags"            : (),
                "title"           : "avatar",
                "type"            : "avatar",
                "user"            : user,
                "width"           : 0,
                "x_restrict"      : 0,
            }
            works = itertools.chain((avatar,), works)

        return works


class PixivMeExtractor(PixivExtractor):
    """Extractor for pixiv.me URLs"""
    subcategory = "me"
    pattern = r"(?:https?://)?pixiv\.me/([^/?#]+)"
    test = (
        ("https://pixiv.me/del_shannon", {
            "url": "29c295ce75150177e6b0a09089a949804c708fbf",
        }),
        ("https://pixiv.me/del_shanno", {
            "exception": exception.NotFoundError,
        }),
    )

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.account = match.group(1)

    def items(self):
        url = "https://pixiv.me/" + self.account
        data = {"_extractor": PixivUserExtractor}
        response = self.request(
            url, method="HEAD", allow_redirects=False, notfound="user")
        yield Message.Version, 1
        yield Message.Queue, response.headers["Location"], data


class PixivWorkExtractor(PixivExtractor):
    """Extractor for a single pixiv work/illustration"""
    subcategory = "work"
    pattern = (r"(?:https?://)?(?:(?:www\.|touch\.)?pixiv\.net"
               r"/(?:(?:en/)?artworks/"
               r"|member_illust\.php\?(?:[^&]+&)*illust_id=)(\d+)"
               r"|(?:i(?:\d+\.pixiv|\.pximg)\.net"
               r"/(?:(?:.*/)?img-[^/]+/img/\d{4}(?:/\d\d){5}|img\d+/img/[^/]+)"
               r"|img\d*\.pixiv\.net/img/[^/]+|(?:www\.)?pixiv\.net/i)/(\d+))")
    test = (
        ("https://www.pixiv.net/artworks/966412", {
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
        # related works (#1237)
        ("https://www.pixiv.net/artworks/966412", {
            "options": (("related", True),),
            "range": "1-10",
            "count": ">= 10",
        }),
        ("https://www.pixiv.net/en/artworks/966412"),
        ("http://www.pixiv.net/member_illust.php?mode=medium&illust_id=96641"),
        ("http://i1.pixiv.net/c/600x600/img-master"
         "/img/2008/06/13/00/29/13/966412_p0_master1200.jpg"),
        ("https://i.pximg.net/img-original"
         "/img/2017/04/25/07/33/29/62568267_p0.png"),
        ("https://www.pixiv.net/i/966412"),
        ("http://img.pixiv.net/img/soundcross/42626136.jpg"),
        ("http://i2.pixiv.net/img76/img/snailrin/42672235.jpg"),
    )

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.illust_id = match.group(1) or match.group(2)

    def works(self):
        works = (self.api.illust_detail(self.illust_id),)
        if self.config("related", False):
            related = self.api.illust_related(self.illust_id)
            works = itertools.chain(works, related)
        return works


class PixivFavoriteExtractor(PixivExtractor):
    """Extractor for all favorites/bookmarks of a pixiv-user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "bookmarks",
                     "{user_bookmark[id]} {user_bookmark[account]}")
    archive_fmt = "f_{user_bookmark[id]}_{id}{num}.{extension}"
    pattern = (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net/(?:(?:en/)?"
               r"users/(\d+)/(bookmarks/artworks|following)(?:/([^/?#]+))?"
               r"|bookmark\.php)(?:\?([^#]*))?")
    test = (
        ("https://www.pixiv.net/en/users/173530/bookmarks/artworks", {
            "url": "e717eb511500f2fa3497aaee796a468ecf685cc4",
        }),
        ("https://www.pixiv.net/bookmark.php?id=173530", {
            "url": "e717eb511500f2fa3497aaee796a468ecf685cc4",
        }),
        # bookmarks with specific tag
        (("https://www.pixiv.net/en/users/3137110"
          "/bookmarks/artworks/%E3%81%AF%E3%82%93%E3%82%82%E3%82%93"), {
            "url": "379b28275f786d946e01f721e54afe346c148a8c",
        }),
        # bookmarks with specific tag (legacy url)
        (("https://www.pixiv.net/bookmark.php?id=3137110"
          "&tag=%E3%81%AF%E3%82%93%E3%82%82%E3%82%93&p=1"), {
            "url": "379b28275f786d946e01f721e54afe346c148a8c",
        }),
        # own bookmarks
        ("https://www.pixiv.net/bookmark.php", {
            "url": "90c1715b07b0d1aad300bce256a0bc71f42540ba",
        }),
        # own bookmarks with tag (#596)
        ("https://www.pixiv.net/bookmark.php?tag=foobar", {
            "count": 0,
        }),
        # followed users (#515)
        ("https://www.pixiv.net/en/users/173530/following", {
            "pattern": PixivUserExtractor.pattern,
            "count": ">= 12",
        }),
        # followed users (legacy url) (#515)
        ("https://www.pixiv.net/bookmark.php?id=173530&type=user", {
            "pattern": PixivUserExtractor.pattern,
            "count": ">= 12",
        }),
        # touch URLs
        ("https://touch.pixiv.net/bookmark.php?id=173530"),
        ("https://touch.pixiv.net/bookmark.php"),
    )

    def __init__(self, match):
        uid, kind, self.tag, query = match.groups()

        if query:
            self.query = text.parse_query(query)
            uid = self.query.get("id")
            if not uid:
                self.subcategory = "bookmark"
            elif self.query.get("type") == "user":
                self.subcategory = "following"
                self.items = self._items_following
        else:
            self.query = {}
            if kind == "following":
                self.subcategory = "following"
                self.items = self._items_following

        PixivExtractor.__init__(self, match)
        self.user_id = uid

    def works(self):
        tag = None
        restrict = "public"

        if "tag" in self.query:
            tag = text.unquote(self.query["tag"])
        elif self.tag:
            tag = text.unquote(self.tag)

        if "rest" in self.query and self.query["rest"] == "hide":
            restrict = "private"

        return self.api.user_bookmarks_illust(self.user_id, tag, restrict)

    def metadata(self):
        if self.user_id:
            user = self.api.user_detail(self.user_id)
        else:
            self.api.login()
            user = self.api.user

        self.user_id = user["id"]
        return {"user_bookmark": user}

    def _items_following(self):
        yield Message.Version, 1

        for preview in self.api.user_following(self.user_id):
            user = preview["user"]
            user["_extractor"] = PixivUserExtractor
            url = "https://www.pixiv.net/users/{}".format(user["id"])
            yield Message.Queue, url, user


class PixivRankingExtractor(PixivExtractor):
    """Extractor for pixiv ranking pages"""
    subcategory = "ranking"
    archive_fmt = "r_{ranking[mode]}_{ranking[date]}_{id}{num}.{extension}"
    directory_fmt = ("{category}", "rankings",
                     "{ranking[mode]}", "{ranking[date]}")
    pattern = (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/ranking\.php(?:\?([^#]*))?")
    test = (
        ("https://www.pixiv.net/ranking.php?mode=daily&date=20170818"),
        ("https://www.pixiv.net/ranking.php"),
        ("https://touch.pixiv.net/ranking.php"),
    )

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.query = match.group(1)
        self.mode = self.date = None

    def works(self):
        return self.api.illust_ranking(self.mode, self.date)

    def metadata(self):
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
    directory_fmt = ("{category}", "search", "{search[word]}")
    pattern = (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/(?:(?:en/)?tags/([^/?#]+)(?:/[^/?#]+)?/?"
               r"|search\.php)(?:\?([^#]+))?")
    test = (
        ("https://www.pixiv.net/en/tags/Original", {
            "range": "1-10",
            "count": 10,
        }),
        ("https://www.pixiv.net/en/tags/foo/artworks?order=date&s_mode=s_tag"),
        ("https://www.pixiv.net/search.php?s_mode=s_tag&word=Original"),
        ("https://touch.pixiv.net/search.php?word=Original"),
    )

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.word, self.query = match.groups()
        self.sort = self.target = None

    def works(self):
        return self.api.search_illust(self.word, self.sort, self.target)

    def metadata(self):
        query = text.parse_query(self.query)

        if self.word:
            self.word = text.unquote(self.word)
        else:
            if "word" not in query:
                raise exception.StopExtraction("Missing search term")
            self.word = query["word"]

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
    directory_fmt = ("{category}", "following")
    pattern = (r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
               r"/bookmark_new_illust\.php")
    test = (
        ("https://www.pixiv.net/bookmark_new_illust.php"),
        ("https://touch.pixiv.net/bookmark_new_illust.php"),
    )

    def works(self):
        return self.api.illust_follow()

    def metadata(self):
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
    HASH_SECRET = ("28c1fdd170a5204386cb1313c7077b34"
                   "f83e4aaf4aa829ce78c231e05b0bae2c")

    def __init__(self, extractor):
        self.extractor = extractor
        self.log = extractor.log
        self.username = extractor._get_auth_info()[0]
        self.user = None

        extractor.session.headers.update({
            "App-OS"        : "ios",
            "App-OS-Version": "13.1.2",
            "App-Version"   : "7.7.6",
            "User-Agent"    : "PixivIOSApp/7.7.6 (iOS 13.1.2; iPhone11,8)",
            "Referer"       : "https://app-api.pixiv.net/",
        })

        self.client_id = extractor.config(
            "client-id", self.CLIENT_ID)
        self.client_secret = extractor.config(
            "client-secret", self.CLIENT_SECRET)

        token = extractor.config("refresh-token")
        if token is None or token == "cache":
            token = _refresh_token_cache(self.username)
        self.refresh_token = token

    def login(self):
        """Login and gain an access token"""
        self.user, auth = self._login_impl(self.username)
        self.extractor.session.headers["Authorization"] = auth

    @cache(maxage=3600, keyarg=1)
    def _login_impl(self, username):
        if not self.refresh_token:
            raise exception.AuthenticationError(
                "'refresh-token' required.\n"
                "Run `gallery-dl oauth:pixiv` to get one.")

        self.log.info("Refreshing access token")
        url = "https://oauth.secure.pixiv.net/auth/token"
        data = {
            "client_id"     : self.client_id,
            "client_secret" : self.client_secret,
            "grant_type"    : "refresh_token",
            "refresh_token" : self.refresh_token,
            "get_secure_url": "1",
        }

        time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        headers = {
            "X-Client-Time": time,
            "X-Client-Hash": hashlib.md5(
                (time + self.HASH_SECRET).encode()).hexdigest(),
        }

        response = self.extractor.request(
            url, method="POST", headers=headers, data=data, fatal=False)
        if response.status_code >= 400:
            self.log.debug(response.text)
            raise exception.AuthenticationError("Invalid refresh token")

        data = response.json()["response"]
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

    def illust_related(self, illust_id):
        params = {"illust_id": illust_id}
        return self._pagination("v2/illust/related", params)

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

    def user_following(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("v1/user/following", params, "user_previews")

    def user_illusts(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("v1/user/illusts", params)

    def ugoira_metadata(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("v1/ugoira/metadata", params)["ugoira_metadata"]

    def _call(self, endpoint, params=None):
        url = "https://app-api.pixiv.net/" + endpoint

        self.login()
        response = self.extractor.request(url, params=params, fatal=False)
        data = response.json()

        if "error" in data:
            if response.status_code == 404:
                raise exception.NotFoundError()

            error = data["error"]
            if "rate limit" in (error.get("message") or "").lower():
                self.log.info("Waiting two minutes for API rate limit reset.")
                time.sleep(120)
                return self._call(endpoint, params)
            raise exception.StopExtraction("API request failed: %s", error)

        return data

    def _pagination(self, endpoint, params, key="illusts"):
        while True:
            data = self._call(endpoint, params)
            yield from data[key]

            if not data["next_url"]:
                return
            query = data["next_url"].rpartition("?")[2]
            params = text.parse_query(query)


@cache(maxage=10*365*24*3600, keyarg=0)
def _refresh_token_cache(username):
    return None
