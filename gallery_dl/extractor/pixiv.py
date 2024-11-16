# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.pixiv.net/"""

from .common import Extractor, Message
from .. import text, util, exception
from ..cache import cache, memcache
from datetime import datetime, timedelta
import itertools
import hashlib

BASE_PATTERN = r"(?:https?://)?(?:www\.|touch\.)?pixiv\.net"
USER_PATTERN = BASE_PATTERN + r"/(?:en/)?users/(\d+)"


class PixivExtractor(Extractor):
    """Base class for pixiv extractors"""
    category = "pixiv"
    root = "https://www.pixiv.net"
    directory_fmt = ("{category}", "{user[id]} {user[account]}")
    filename_fmt = "{id}_p{num}.{extension}"
    archive_fmt = "{id}{suffix}.{extension}"
    cookies_domain = ".pixiv.net"
    sanity_url = "https://s.pximg.net/common/images/limit_sanity_level_360.png"
    mypixiv_url = "https://s.pximg.net/common/images/limit_mypixiv_360.png"

    def _init(self):
        self.api = PixivAppAPI(self)
        self.load_ugoira = self.config("ugoira", True)
        self.load_ugoira_original = (self.load_ugoira == "original")
        self.max_posts = self.config("max-posts", 0)
        self.sanity_workaround = self.config("sanity", True)
        self.meta_user = self.config("metadata")
        self.meta_bookmark = self.config("metadata-bookmark")
        self.meta_comments = self.config("comments")
        self.meta_captions = self.config("captions")

    def items(self):
        tags = self.config("tags", "japanese")
        if tags == "original":
            transform_tags = None
        elif tags == "translated":
            def transform_tags(work):
                work["tags"] = list(dict.fromkeys(
                    tag["translated_name"] or tag["name"]
                    for tag in work["tags"]))
        else:
            def transform_tags(work):
                work["tags"] = [tag["name"] for tag in work["tags"]]

        ratings = {0: "General", 1: "R-18", 2: "R-18G"}
        metadata = self.metadata()

        works = self.works()
        if self.max_posts:
            works = itertools.islice(works, self.max_posts)
        for work in works:
            if not work["user"]["id"]:
                continue

            files = self._extract_files(work)

            if self.meta_user:
                work.update(self.api.user_detail(work["user"]["id"]))
            if self.meta_comments:
                if work["total_comments"]:
                    work["comments"] = list(
                        self.api.illust_comments(work["id"]))
                else:
                    work["comments"] = ()
            if self.meta_bookmark and work["is_bookmarked"]:
                detail = self.api.illust_bookmark_detail(work["id"])
                work["tags_bookmark"] = [tag["name"] for tag in detail["tags"]
                                         if tag["is_registered"]]
            if self.meta_captions and not work.get("caption") and \
                    not work.get("_mypixiv") and not work.get("_ajax"):
                body = self._request_ajax("/illust/" + str(work["id"]))
                if body:
                    work["caption"] = text.unescape(body["illustComment"])

            if transform_tags:
                transform_tags(work)
            work["num"] = 0
            work["date"] = text.parse_datetime(work["create_date"])
            work["rating"] = ratings.get(work["x_restrict"])
            work["suffix"] = ""
            work.update(metadata)

            yield Message.Directory, work
            for work["num"], file in enumerate(files):
                url = file["url"]
                work.update(file)
                work["date_url"] = self._date_from_url(url)
                yield Message.Url, url, text.nameext_from_url(url, work)

    def _extract_files(self, work):
        meta_single_page = work["meta_single_page"]
        meta_pages = work["meta_pages"]
        del work["meta_single_page"]
        del work["image_urls"]
        del work["meta_pages"]

        if meta_pages:
            return [
                {
                    "url"   : img["image_urls"]["original"],
                    "suffix": "_p{:02}".format(num),
                }
                for num, img in enumerate(meta_pages)
            ]

        url = meta_single_page["original_image_url"]
        if url == self.sanity_url:
            work["_ajax"] = True
            self.log.warning("%s: 'limit_sanity_level' warning", work["id"])
            if self.sanity_workaround:
                body = self._request_ajax("/illust/" + str(work["id"]))
                return self._extract_ajax(work, body)

        elif url == self.mypixiv_url:
            work["_mypixiv"] = True
            self.log.warning("%s: 'My pixiv' locked", work["id"])

        elif work["type"] != "ugoira":
            return ({"url": url},)

        elif self.load_ugoira:
            try:
                return self._extract_ugoira(work, url)
            except Exception as exc:
                self.log.warning(
                    "%s: Unable to retrieve Ugoira metatdata (%s - %s)",
                    work["id"], exc.__class__.__name__, exc)

        return ()

    def _extract_ugoira(self, work, img_url):
        ugoira = self.api.ugoira_metadata(work["id"])
        work["_ugoira_frame_data"] = work["frames"] = frames = ugoira["frames"]
        work["_ugoira_original"] = self.load_ugoira_original
        work["_http_adjust_extension"] = False

        if self.load_ugoira_original:
            work["date_url"] = self._date_from_url(img_url)

            base, sep, ext = img_url.rpartition("_ugoira0.")
            if sep:
                base += "_ugoira"
            else:
                base, sep, _ = img_url.rpartition("_ugoira")
                base = base.replace(
                    "/img-zip-ugoira/", "/img-original/", 1) + sep

                for ext in ("jpg", "png", "gif"):
                    try:
                        url = "{}0.{}".format(base, ext)
                        self.request(url, method="HEAD")
                        break
                    except exception.HttpError:
                        pass
                else:
                    self.log.warning(
                        "Unable to find Ugoira frame URLs (%s)", work["id"])

            return [
                {
                    "url": "{}{}.{}".format(base, num, ext),
                    "suffix": "_p{:02}".format(num),
                    "_ugoira_frame_index": num,
                }
                for num in range(len(frames))
            ]

        else:
            zip_url = ugoira["zip_urls"]["medium"]
            work["date_url"] = self._date_from_url(zip_url)
            url = zip_url.replace("_ugoira600x600", "_ugoira1920x1080", 1)
            return ({"url": url},)

    def _request_ajax(self, endpoint):
        url = "{}/ajax{}".format(self.root, endpoint)
        try:
            return self.request(url, headers=self.headers_web).json()["body"]
        except Exception:
            return None

    def _extract_ajax(self, work, body):
        work["_ajax"] = True
        url = self._extract_ajax_url(body)
        if not url:
            return ()

        for key_app, key_ajax in (
            ("title"            , "illustTitle"),
            ("image_urls"       , "urls"),
            ("create_date"      , "createDate"),
            ("width"            , "width"),
            ("height"           , "height"),
            ("sanity_level"     , "sl"),
            ("total_view"       , "viewCount"),
            ("total_comments"   , "commentCount"),
            ("total_bookmarks"  , "bookmarkCount"),
            ("restrict"         , "restrict"),
            ("x_restrict"       , "xRestrict"),
            ("illust_ai_type"   , "aiType"),
            ("illust_book_style", "bookStyle"),
        ):
            work[key_app] = body[key_ajax]

        work["user"] = {
            "account"    : body["userAccount"],
            "id"         : int(body["userId"]),
            "is_followed": False,
            "name"       : body["userName"],
            "profile_image_urls": {},
        }

        work["tags"] = tags = []
        for tag in body["tags"]["tags"]:
            name = tag["tag"]
            try:
                translated_name = tag["translation"]["en"]
            except Exception:
                translated_name = None
            tags.append({"name": name, "translated_name": translated_name})

        work["caption"] = text.unescape(body["illustComment"])
        work["page_count"] = count = body["pageCount"]
        if count == 1:
            return ({"url": url},)

        base, _, ext = url.rpartition("_p0.")
        return [
            {
                "url"   : "{}_p{}.{}".format(base, num, ext),
                "suffix": "_p{:02}".format(num),
            }
            for num in range(count)
        ]

    def _extract_ajax_url(self, body):
        try:
            original = body["urls"]["original"]
            if original:
                return original
        except Exception:
            pass

        try:
            square1200 = body["userIllusts"][body["id"]]["url"]
        except Exception:
            return
        parts = square1200.rpartition("_p0")[0].split("/")
        del parts[3:5]
        parts[3] = "img-original"
        base = "/".join(parts)

        for ext in ("jpg", "png", "gif"):
            try:
                url = "{}_p0.{}".format(base, ext)
                self.request(url, method="HEAD")
                return url
            except exception.HttpError:
                pass

    @staticmethod
    def _date_from_url(url, offset=timedelta(hours=9)):
        try:
            _, _, _, _, _, y, m, d, H, M, S, _ = url.split("/")
            return datetime(
                int(y), int(m), int(d), int(H), int(M), int(S)) - offset
        except Exception:
            return None

    @staticmethod
    def _make_work(kind, url, user):
        p = url.split("/")
        return {
            "create_date"     : "{}-{}-{}T{}:{}:{}+09:00".format(
                p[5], p[6], p[7], p[8], p[9], p[10]) if len(p) > 9 else None,
            "height"          : 0,
            "id"              : kind,
            "image_urls"      : None,
            "meta_pages"      : (),
            "meta_single_page": {"original_image_url": url},
            "page_count"      : 1,
            "sanity_level"    : 0,
            "tags"            : (),
            "title"           : kind,
            "type"            : kind,
            "user"            : user,
            "width"           : 0,
            "x_restrict"      : 0,
        }

    def works(self):
        """Return an iterable containing all relevant 'work' objects"""

    def metadata(self):
        """Collect metadata for extractor job"""
        return {}


class PixivUserExtractor(PixivExtractor):
    """Extractor for a pixiv user profile"""
    subcategory = "user"
    pattern = (BASE_PATTERN + r"/(?:"
               r"(?:en/)?u(?:sers)?/|member\.php\?id=|(?:mypage\.php)?#id="
               r")(\d+)(?:$|[?#])")
    example = "https://www.pixiv.net/en/users/12345"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.user_id = match.group(1)

    def initialize(self):
        pass

    def items(self):
        base = "{}/users/{}/".format(self.root, self.user_id)
        return self._dispatch_extractors((
            (PixivAvatarExtractor       , base + "avatar"),
            (PixivBackgroundExtractor   , base + "background"),
            (PixivArtworksExtractor     , base + "artworks"),
            (PixivFavoriteExtractor     , base + "bookmarks/artworks"),
            (PixivNovelBookmarkExtractor, base + "bookmarks/novels"),
            (PixivNovelUserExtractor    , base + "novels"),
        ), ("artworks",))


class PixivArtworksExtractor(PixivExtractor):
    """Extractor for artworks of a pixiv user"""
    subcategory = "artworks"
    pattern = (BASE_PATTERN + r"/(?:"
               r"(?:en/)?users/(\d+)/(?:artworks|illustrations|manga)"
               r"(?:/([^/?#]+))?/?(?:$|[?#])"
               r"|member_illust\.php\?id=(\d+)(?:&([^#]+))?)")
    example = "https://www.pixiv.net/en/users/12345/artworks"
    _warn_phpsessid = True

    def _init(self):
        PixivExtractor._init(self)

        u1, t1, u2, t2 = self.groups
        if t1:
            t1 = text.unquote(t1)
        elif t2:
            t2 = text.parse_query(t2).get("tag")
        self.user_id = u1 or u2
        self.tag = t1 or t2

        if self.sanity_workaround:
            self.cookies_domain = domain = ".pixiv.net"
            self._init_cookies()
            if self._warn_phpsessid:
                PixivArtworksExtractor._warn_phpsessid = False
                if not self.cookies.get("PHPSESSID", domain=domain):
                    self.log.warning("No 'PHPSESSID' cookie set. Can detect on"
                                     "ly non R-18 'limit_sanity_level' works.")

    def metadata(self):
        if self.config("metadata"):
            self.api.user_detail(self.user_id)
        return {}

    def works(self):
        works = self.api.user_illusts(self.user_id)

        if self.sanity_workaround:
            body = self._request_ajax(
                "/user/{}/profile/all".format(self.user_id))
            try:
                ajax_ids = list(map(int, body["illusts"]))
                ajax_ids.extend(map(int, body["manga"]))
                ajax_ids.sort()
            except Exception as exc:
                self.log.warning("Unable to collect artwork IDs using AJAX "
                                 "API (%s: %s)", exc.__class__.__name__, exc)
            else:
                works = self._extend_sanity(works, ajax_ids)

        if self.tag:
            tag = self.tag.lower()
            works = (
                work for work in works
                if tag in [t["name"].lower() for t in work["tags"]]
            )

        return works

    def _extend_sanity(self, works, ajax_ids):
        user = {"id": 1}
        index = len(ajax_ids) - 1

        for work in works:
            while index >= 0:
                work_id = work["id"]
                ajax_id = ajax_ids[index]

                if ajax_id == work_id:
                    index -= 1
                    break

                elif ajax_id > work_id:
                    index -= 1
                    self.log.debug("Inserting work %s", ajax_id)
                    yield self._make_work(ajax_id, self.sanity_url, user)

                else:  # ajax_id < work_id
                    break

            yield work

        while index >= 0:
            ajax_id = ajax_ids[index]
            self.log.debug("Inserting work %s", ajax_id)
            yield self._make_work(ajax_id, self.sanity_url, user)
            index -= 1


class PixivAvatarExtractor(PixivExtractor):
    """Extractor for pixiv avatars"""
    subcategory = "avatar"
    filename_fmt = "avatar{date:?_//%Y-%m-%d}.{extension}"
    archive_fmt = "avatar_{user[id]}_{date}"
    pattern = USER_PATTERN + r"/avatar"
    example = "https://www.pixiv.net/en/users/12345/avatar"

    def _init(self):
        PixivExtractor._init(self)
        self.sanity_workaround = self.meta_comments = False

    def works(self):
        user = self.api.user_detail(self.groups[0])["user"]
        url = user["profile_image_urls"]["medium"].replace("_170.", ".")
        return (self._make_work("avatar", url, user),)


class PixivBackgroundExtractor(PixivExtractor):
    """Extractor for pixiv background banners"""
    subcategory = "background"
    filename_fmt = "background{date:?_//%Y-%m-%d}.{extension}"
    archive_fmt = "background_{user[id]}_{date}"
    pattern = USER_PATTERN + "/background"
    example = "https://www.pixiv.net/en/users/12345/background"

    def _init(self):
        PixivExtractor._init(self)
        self.sanity_workaround = self.meta_comments = False

    def works(self):
        detail = self.api.user_detail(self.groups[0])
        url = detail["profile"]["background_image_url"]
        if not url:
            return ()
        if "/c/" in url:
            parts = url.split("/")
            del parts[3:5]
            url = "/".join(parts)
        url = url.replace("_master1200.", ".")
        work = self._make_work("background", url, detail["user"])
        if url.endswith(".jpg"):
            url = url[:-4]
            work["_fallback"] = (url + ".png", url + ".gif")
        return (work,)


class PixivMeExtractor(PixivExtractor):
    """Extractor for pixiv.me URLs"""
    subcategory = "me"
    pattern = r"(?:https?://)?pixiv\.me/([^/?#]+)"
    example = "https://pixiv.me/USER"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.account = match.group(1)

    def items(self):
        url = "https://pixiv.me/" + self.account
        data = {"_extractor": PixivUserExtractor}
        response = self.request(
            url, method="HEAD", allow_redirects=False, notfound="user")
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
    example = "https://www.pixiv.net/artworks/12345"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.illust_id = match.group(1) or match.group(2)

    def works(self):
        works = (self.api.illust_detail(self.illust_id),)
        if self.config("related", False):
            related = self.api.illust_related(self.illust_id)
            works = itertools.chain(works, related)
        return works


class PixivUnlistedExtractor(PixivExtractor):
    """Extractor for a unlisted pixiv illustrations"""
    subcategory = "unlisted"
    pattern = BASE_PATTERN + r"/(?:en/)?artworks/unlisted/(\w+)"
    example = "https://www.pixiv.net/en/artworks/unlisted/a1b2c3d4e5f6g7h8i9j0"

    def _extract_files(self, work):
        body = self._request_ajax("/illust/unlisted/" + work["id"])
        work["id_unlisted"] = work["id"]
        work["id"] = text.parse_int(body["illustId"])
        return self._extract_ajax(work, body)

    def works(self):
        return ({"id": self.groups[0], "user": {"id": 1}},)


class PixivFavoriteExtractor(PixivExtractor):
    """Extractor for all favorites/bookmarks of a pixiv user"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "bookmarks",
                     "{user_bookmark[id]} {user_bookmark[account]}")
    archive_fmt = "f_{user_bookmark[id]}_{id}{num}.{extension}"
    pattern = (BASE_PATTERN + r"/(?:(?:en/)?"
               r"users/(\d+)/(bookmarks/artworks|following)(?:/([^/?#]+))?"
               r"|bookmark\.php)(?:\?([^#]*))?")
    example = "https://www.pixiv.net/en/users/12345/bookmarks/artworks"

    def __init__(self, match):
        uid, kind, self.tag, query = match.groups()
        query = text.parse_query(query)

        if not uid:
            uid = query.get("id")
            if not uid:
                self.subcategory = "bookmark"

        if kind == "following" or query.get("type") == "user":
            self.subcategory = "following"
            self.items = self._items_following

        PixivExtractor.__init__(self, match)
        self.query = query
        self.user_id = uid

    def works(self):
        tag = None
        if "tag" in self.query:
            tag = text.unquote(self.query["tag"])
        elif self.tag:
            tag = text.unquote(self.tag)

        restrict = "public"
        if self.query.get("rest") == "hide":
            restrict = "private"

        return self.api.user_bookmarks_illust(self.user_id, tag, restrict)

    def metadata(self):
        if self.user_id:
            user = self.api.user_detail(self.user_id)["user"]
        else:
            self.api.login()
            user = self.api.user

        self.user_id = user["id"]
        return {"user_bookmark": user}

    def _items_following(self):
        restrict = "public"
        if self.query.get("rest") == "hide":
            restrict = "private"

        for preview in self.api.user_following(self.user_id, restrict):
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
    pattern = BASE_PATTERN + r"/ranking\.php(?:\?([^#]*))?"
    example = "https://www.pixiv.net/ranking.php"

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
            "daily_ai": "day_ai",
            "daily_r18_ai": "day_r18_ai",
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
        try:
            self.mode = mode = mode_map[mode]
        except KeyError:
            raise exception.StopExtraction("Invalid mode '%s'", mode)

        date = query.get("date")
        if date:
            if len(date) == 8 and date.isdecimal():
                date = "{}-{}-{}".format(date[0:4], date[4:6], date[6:8])
            else:
                self.log.warning("invalid date '%s'", date)
                date = None
        if not date:
            now = util.datetime_utcnow()
            date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
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
    pattern = (BASE_PATTERN + r"/(?:(?:en/)?tags/([^/?#]+)(?:/[^/?#]+)?/?"
               r"|search\.php)(?:\?([^#]+))?")
    example = "https://www.pixiv.net/en/tags/TAG"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.word, self.query = match.groups()
        self.sort = self.target = None

    def works(self):
        return self.api.search_illust(
            self.word, self.sort, self.target,
            date_start=self.date_start, date_end=self.date_end)

    def metadata(self):
        query = text.parse_query(self.query)

        if self.word:
            self.word = text.unquote(self.word)
        else:
            try:
                self.word = query["word"]
            except KeyError:
                raise exception.StopExtraction("Missing search term")

        sort = query.get("order", "date_d")
        sort_map = {
            "date": "date_asc",
            "date_d": "date_desc",
            "popular_d": "popular_desc",
            "popular_male_d": "popular_male_desc",
            "popular_female_d": "popular_female_desc",
        }
        try:
            self.sort = sort = sort_map[sort]
        except KeyError:
            raise exception.StopExtraction("Invalid search order '%s'", sort)

        target = query.get("s_mode", "s_tag_full")
        target_map = {
            "s_tag": "partial_match_for_tags",
            "s_tag_full": "exact_match_for_tags",
            "s_tc": "title_and_caption",
        }
        try:
            self.target = target = target_map[target]
        except KeyError:
            raise exception.StopExtraction("Invalid search mode '%s'", target)

        self.date_start = query.get("scd")
        self.date_end = query.get("ecd")

        return {"search": {
            "word": self.word,
            "sort": self.sort,
            "target": self.target,
            "date_start": self.date_start,
            "date_end": self.date_end,
        }}


class PixivFollowExtractor(PixivExtractor):
    """Extractor for new illustrations from your followed artists"""
    subcategory = "follow"
    archive_fmt = "F_{user_follow[id]}_{id}{num}.{extension}"
    directory_fmt = ("{category}", "following")
    pattern = BASE_PATTERN + r"/bookmark_new_illust\.php"
    example = "https://www.pixiv.net/bookmark_new_illust.php"

    def works(self):
        return self.api.illust_follow()

    def metadata(self):
        self.api.login()
        return {"user_follow": self.api.user}


class PixivPixivisionExtractor(PixivExtractor):
    """Extractor for illustrations from a pixivision article"""
    subcategory = "pixivision"
    directory_fmt = ("{category}", "pixivision",
                     "{pixivision_id} {pixivision_title}")
    archive_fmt = "V{pixivision_id}_{id}{suffix}.{extension}"
    pattern = r"(?:https?://)?(?:www\.)?pixivision\.net/(?:en/)?a/(\d+)"
    example = "https://www.pixivision.net/en/a/12345"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.pixivision_id = match.group(1)

    def works(self):
        return (
            self.api.illust_detail(illust_id.partition("?")[0])
            for illust_id in util.unique_sequence(text.extract_iter(
                self.page, '<a href="https://www.pixiv.net/en/artworks/', '"'))
        )

    def metadata(self):
        url = "https://www.pixivision.net/en/a/" + self.pixivision_id
        headers = {"User-Agent": "Mozilla/5.0"}
        self.page = self.request(url, headers=headers).text

        title = text.extr(self.page, '<title>', '<')
        return {
            "pixivision_id"   : self.pixivision_id,
            "pixivision_title": text.unescape(title),
        }


class PixivSeriesExtractor(PixivExtractor):
    """Extractor for illustrations from a Pixiv series"""
    subcategory = "series"
    directory_fmt = ("{category}", "{user[id]} {user[account]}",
                     "{series[id]} {series[title]}")
    filename_fmt = "{num_series:>03}_{id}_p{num}.{extension}"
    pattern = BASE_PATTERN + r"/user/(\d+)/series/(\d+)"
    example = "https://www.pixiv.net/user/12345/series/12345"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.user_id, self.series_id = match.groups()

    def works(self):
        series = None

        for work in self.api.illust_series(self.series_id):
            if series is None:
                series = self.api.data
                series["total"] = num_series = series.pop("series_work_count")
            else:
                num_series -= 1

            work["num_series"] = num_series
            work["series"] = series
            yield work


class PixivNovelExtractor(PixivExtractor):
    """Extractor for pixiv novels"""
    subcategory = "novel"
    request_interval = (0.5, 1.5)
    pattern = BASE_PATTERN + r"/n(?:ovel/show\.php\?id=|/)(\d+)"
    example = "https://www.pixiv.net/novel/show.php?id=12345"

    def __init__(self, match):
        PixivExtractor.__init__(self, match)
        self.novel_id = match.group(1)

    def items(self):
        tags = self.config("tags", "japanese")
        if tags == "original":
            transform_tags = None
        elif tags == "translated":
            def transform_tags(work):
                work["tags"] = list(dict.fromkeys(
                    tag["translated_name"] or tag["name"]
                    for tag in work["tags"]))
        else:
            def transform_tags(work):
                work["tags"] = [tag["name"] for tag in work["tags"]]

        ratings = {0: "General", 1: "R-18", 2: "R-18G"}
        embeds = self.config("embeds")
        covers = self.config("covers")

        if embeds:
            headers = {
                "User-Agent"    : "Mozilla/5.0",
                "App-OS"        : None,
                "App-OS-Version": None,
                "App-Version"   : None,
                "Referer"       : self.root + "/",
                "Authorization" : None,
            }

        novels = self.novels()
        if self.max_posts:
            novels = itertools.islice(novels, self.max_posts)
        for novel in novels:
            if self.meta_user:
                novel.update(self.api.user_detail(novel["user"]["id"]))
            if self.meta_comments:
                if novel["total_comments"]:
                    novel["comments"] = list(
                        self.api.novel_comments(novel["id"]))
                else:
                    novel["comments"] = ()
            if self.meta_bookmark and novel["is_bookmarked"]:
                detail = self.api.novel_bookmark_detail(novel["id"])
                novel["tags_bookmark"] = [tag["name"] for tag in detail["tags"]
                                          if tag["is_registered"]]
            if transform_tags:
                transform_tags(novel)
            novel["num"] = 0
            novel["date"] = text.parse_datetime(novel["create_date"])
            novel["rating"] = ratings.get(novel["x_restrict"])
            novel["suffix"] = ""

            yield Message.Directory, novel

            try:
                content = self.api.novel_webview(novel["id"])["text"]
            except Exception:
                self.log.warning("Unable to download novel %s", novel["id"])
                continue

            novel["extension"] = "txt"
            yield Message.Url, "text:" + content, novel

            if covers:
                path = novel["image_urls"]["large"].partition("/img/")[2]
                url = ("https://i.pximg.net/novel-cover-original/img/" +
                       path.rpartition(".")[0].replace("_master1200", ""))
                novel["date_url"] = self._date_from_url(url)
                novel["num"] += 1
                novel["suffix"] = "_p{:02}".format(novel["num"])
                novel["_fallback"] = (url + ".png",)
                url_jpg = url + ".jpg"
                text.nameext_from_url(url_jpg, novel)
                yield Message.Url, url_jpg, novel
                del novel["_fallback"]

            if embeds:
                desktop = False
                illusts = {}

                for marker in text.extract_iter(content, "[", "]"):
                    if marker.startswith("uploadedimage:"):
                        desktop = True
                    elif marker.startswith("pixivimage:"):
                        illusts[marker[11:].partition("-")[0]] = None

                if desktop:
                    novel_id = str(novel["id"])
                    url = "{}/novel/show.php?id={}".format(
                        self.root, novel_id)
                    data = util.json_loads(text.extr(
                        self.request(url, headers=headers).text,
                        "id=\"meta-preload-data\" content='", "'"))

                    for image in (data["novel"][novel_id]
                                  ["textEmbeddedImages"]).values():
                        url = image.pop("urls")["original"]
                        novel.update(image)
                        novel["date_url"] = self._date_from_url(url)
                        novel["num"] += 1
                        novel["suffix"] = "_p{:02}".format(novel["num"])
                        text.nameext_from_url(url, novel)
                        yield Message.Url, url, novel

                if illusts:
                    novel["_extractor"] = PixivWorkExtractor
                    novel["date_url"] = None
                    for illust_id in illusts:
                        novel["num"] += 1
                        novel["suffix"] = "_p{:02}".format(novel["num"])
                        url = "{}/artworks/{}".format(self.root, illust_id)
                        yield Message.Queue, url, novel

    def novels(self):
        novel = self.api.novel_detail(self.novel_id)
        if self.config("full-series") and novel["series"]:
            self.subcategory = PixivNovelSeriesExtractor.subcategory
            return self.api.novel_series(novel["series"]["id"])
        return (novel,)


class PixivNovelUserExtractor(PixivNovelExtractor):
    """Extractor for pixiv users' novels"""
    subcategory = "novel-user"
    pattern = USER_PATTERN + r"/novels"
    example = "https://www.pixiv.net/en/users/12345/novels"

    def novels(self):
        return self.api.user_novels(self.novel_id)


class PixivNovelSeriesExtractor(PixivNovelExtractor):
    """Extractor for pixiv novel series"""
    subcategory = "novel-series"
    pattern = BASE_PATTERN + r"/novel/series/(\d+)"
    example = "https://www.pixiv.net/novel/series/12345"

    def novels(self):
        return self.api.novel_series(self.novel_id)


class PixivNovelBookmarkExtractor(PixivNovelExtractor):
    """Extractor for bookmarked pixiv novels"""
    subcategory = "novel-bookmark"
    pattern = (USER_PATTERN + r"/bookmarks/novels"
               r"(?:/([^/?#]+))?(?:/?\?([^#]+))?")
    example = "https://www.pixiv.net/en/users/12345/bookmarks/novels"

    def __init__(self, match):
        PixivNovelExtractor.__init__(self, match)
        self.user_id, self.tag, self.query = match.groups()

    def novels(self):
        if self.tag:
            tag = text.unquote(self.tag)
        else:
            tag = None

        if text.parse_query(self.query).get("rest") == "hide":
            restrict = "private"
        else:
            restrict = "public"

        return self.api.user_bookmarks_novel(self.user_id, tag, restrict)


class PixivSketchExtractor(Extractor):
    """Extractor for user pages on sketch.pixiv.net"""
    category = "pixiv"
    subcategory = "sketch"
    directory_fmt = ("{category}", "sketch", "{user[unique_name]}")
    filename_fmt = "{post_id} {id}.{extension}"
    archive_fmt = "S{user[id]}_{id}"
    root = "https://sketch.pixiv.net"
    cookies_domain = ".pixiv.net"
    pattern = r"(?:https?://)?sketch\.pixiv\.net/@([^/?#]+)"
    example = "https://sketch.pixiv.net/@USER"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.username = match.group(1)

    def items(self):
        headers = {"Referer": "{}/@{}".format(self.root, self.username)}

        for post in self.posts():
            media = post["media"]
            post["post_id"] = post["id"]
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
            util.delete_items(post, ("id", "media", "_links"))

            yield Message.Directory, post
            post["_http_headers"] = headers

            for photo in media:
                original = photo["photo"]["original"]
                post["id"] = photo["id"]
                post["width"] = original["width"]
                post["height"] = original["height"]

                url = original["url"]
                text.nameext_from_url(url, post)
                yield Message.Url, url, post

    def posts(self):
        url = "{}/api/walls/@{}/posts/public.json".format(
            self.root, self.username)
        headers = {
            "Accept": "application/vnd.sketch-v4+json",
            "X-Requested-With": "{}/@{}".format(self.root, self.username),
            "Referer": self.root + "/",
        }

        while True:
            data = self.request(url, headers=headers).json()
            yield from data["data"]["items"]

            next_url = data["_links"].get("next")
            if not next_url:
                return
            url = self.root + next_url["href"]


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

        extractor.headers_web = extractor.session.headers.copy()
        extractor.session.headers.update({
            "App-OS"        : "ios",
            "App-OS-Version": "16.7.2",
            "App-Version"   : "7.19.1",
            "User-Agent"    : "PixivIOSApp/7.19.1 (iOS 16.7.2; iPhone12,8)",
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

        time = util.datetime_utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
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
        return self._call("/v1/illust/detail", params)["illust"]

    def illust_bookmark_detail(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call(
            "/v2/illust/bookmark/detail", params)["bookmark_detail"]

    def illust_comments(self, illust_id):
        params = {"illust_id": illust_id}
        return self._pagination("/v3/illust/comments", params, "comments")

    def illust_follow(self, restrict="all"):
        params = {"restrict": restrict}
        return self._pagination("/v2/illust/follow", params)

    def illust_ranking(self, mode="day", date=None):
        params = {"mode": mode, "date": date}
        return self._pagination("/v1/illust/ranking", params)

    def illust_related(self, illust_id):
        params = {"illust_id": illust_id}
        return self._pagination("/v2/illust/related", params)

    def illust_series(self, series_id, offset=0):
        params = {"illust_series_id": series_id, "offset": offset}
        return self._pagination("/v1/illust/series", params,
                                key_data="illust_series_detail")

    def novel_bookmark_detail(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call(
            "/v2/novel/bookmark/detail", params)["bookmark_detail"]

    def novel_comments(self, novel_id):
        params = {"novel_id": novel_id}
        return self._pagination("/v1/novel/comments", params, "comments")

    def novel_detail(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call("/v2/novel/detail", params)["novel"]

    def novel_series(self, series_id):
        params = {"series_id": series_id}
        return self._pagination("/v1/novel/series", params, "novels")

    def novel_text(self, novel_id):
        params = {"novel_id": novel_id}
        return self._call("/v1/novel/text", params)

    def novel_webview(self, novel_id):
        params = {"id": novel_id, "viewer_version": "20221031_ai"}
        return self._call(
            "/webview/v2/novel", params, self._novel_webview_parse)

    def _novel_webview_parse(self, response):
        return util.json_loads(text.extr(
            response.text, "novel: ", ",\n"))

    def search_illust(self, word, sort=None, target=None, duration=None,
                      date_start=None, date_end=None):
        params = {"word": word, "search_target": target,
                  "sort": sort, "duration": duration,
                  "start_date": date_start, "end_date": date_end}
        return self._pagination("/v1/search/illust", params)

    def user_bookmarks_illust(self, user_id, tag=None, restrict="public"):
        """Return illusts bookmarked by a user"""
        params = {"user_id": user_id, "tag": tag, "restrict": restrict}
        return self._pagination("/v1/user/bookmarks/illust", params)

    def user_bookmarks_novel(self, user_id, tag=None, restrict="public"):
        """Return novels bookmarked by a user"""
        params = {"user_id": user_id, "tag": tag, "restrict": restrict}
        return self._pagination("/v1/user/bookmarks/novel", params, "novels")

    def user_bookmark_tags_illust(self, user_id, restrict="public"):
        """Return bookmark tags defined by a user"""
        params = {"user_id": user_id, "restrict": restrict}
        return self._pagination(
            "/v1/user/bookmark-tags/illust", params, "bookmark_tags")

    @memcache(keyarg=1)
    def user_detail(self, user_id):
        params = {"user_id": user_id}
        return self._call("/v1/user/detail", params)

    def user_following(self, user_id, restrict="public"):
        params = {"user_id": user_id, "restrict": restrict}
        return self._pagination("/v1/user/following", params, "user_previews")

    def user_illusts(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("/v1/user/illusts", params)

    def user_novels(self, user_id):
        params = {"user_id": user_id}
        return self._pagination("/v1/user/novels", params, "novels")

    def ugoira_metadata(self, illust_id):
        params = {"illust_id": illust_id}
        return self._call("/v1/ugoira/metadata", params)["ugoira_metadata"]

    def _call(self, endpoint, params=None, parse=None):
        url = "https://app-api.pixiv.net" + endpoint

        while True:
            self.login()
            response = self.extractor.request(url, params=params, fatal=False)

            if parse:
                data = parse(response)
            else:
                data = response.json()

            if "error" not in data:
                return data

            self.log.debug(data)

            if response.status_code == 404:
                raise exception.NotFoundError()

            error = data["error"]
            if "rate limit" in (error.get("message") or "").lower():
                self.extractor.wait(seconds=300)
                continue

            raise exception.StopExtraction("API request failed: %s", error)

    def _pagination(self, endpoint, params,
                    key_items="illusts", key_data=None):
        while True:
            data = self._call(endpoint, params)

            if key_data:
                self.data = data.get(key_data)
                key_data = None
            yield from data[key_items]

            if not data["next_url"]:
                return
            query = data["next_url"].rpartition("?")[2]
            params = text.parse_query(query)


@cache(maxage=36500*86400, keyarg=0)
def _refresh_token_cache(username):
    return None
