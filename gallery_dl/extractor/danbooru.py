# -*- coding: utf-8 -*-

# Copyright 2014-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/ and other Danbooru instances"""

from .common import BaseExtractor, Message
from ..version import __version__
from .. import text
import datetime


class DanbooruExtractor(BaseExtractor):
    """Base class for danbooru extractors"""
    basecategory = "Danbooru"
    filename_fmt = "{category}_{id}_{filename}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 200

    def __init__(self, match):
        self._init_category(match)

        instance = INSTANCES.get(self.category) or {}
        iget = instance.get

        self.headers = iget("headers")
        self.page_limit = iget("page-limit", 1000)
        self.page_start = iget("page-start")
        self.per_page = iget("per-page", 200)
        self.request_interval_min = iget("request-interval-min", 0.0)
        self._pools = iget("pools")
        self._popular_endpoint = iget("popular", "/explore/posts/popular.json")

        BaseExtractor.__init__(self, match)

        self.ugoira = self.config("ugoira", False)
        self.external = self.config("external", False)
        self.extended_metadata = self.config("metadata", False)

        username, api_key = self._get_auth_info()
        if username:
            self.log.debug("Using HTTP Basic Auth for user '%s'", username)
            self.session.auth = (username, api_key)

    def request(self, url, **kwargs):
        kwargs["headers"] = self.headers
        return BaseExtractor.request(self, url, **kwargs)

    def skip(self, num):
        pages = num // self.per_page
        if pages >= self.page_limit:
            pages = self.page_limit - 1
        self.page_start = pages + 1
        return pages * self.per_page

    def items(self):
        data = self.metadata()
        for post in self.posts():

            file = post.get("file")
            if file:
                url = file["url"]
                if not url:
                    md5 = file["md5"]
                    url = file["url"] = (
                        "https://static1.{}/data/{}/{}/{}.{}".format(
                            self.root[8:], md5[0:2], md5[2:4], md5, file["ext"]
                        ))
                post["filename"] = file["md5"]
                post["extension"] = file["ext"]

            else:
                try:
                    url = post["file_url"]
                except KeyError:
                    if self.external and post["source"]:
                        post.update(data)
                        yield Message.Directory, post
                        yield Message.Queue, post["source"], post
                    continue

                text.nameext_from_url(url, post)

            if post["extension"] == "zip":
                if self.ugoira:
                    post["frames"] = self._ugoira_frames(post)
                    post["_http_adjust_extension"] = False
                else:
                    url = post["large_file_url"]
                    post["extension"] = "webm"

            if self.extended_metadata:
                template = (
                    "{}/posts/{}.json"
                    "?only=artist_commentary,children,notes,parent"
                )
                resp = self.request(template.format(self.root, post["id"]))
                post.update(resp.json())

            post.update(data)
            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def _pagination(self, endpoint, params, pagenum=False):
        url = self.root + endpoint
        params["limit"] = self.per_page
        params["page"] = self.page_start

        while True:
            posts = self.request(url, params=params).json()
            if "posts" in posts:
                posts = posts["posts"]
            yield from posts

            if len(posts) < self.per_page:
                return

            if pagenum:
                params["page"] += 1
            else:
                for post in reversed(posts):
                    if "id" in post:
                        params["page"] = "b{}".format(post["id"])
                        break
                else:
                    return

    def _ugoira_frames(self, post):
        data = self.request("{}/posts/{}.json?only=media_metadata".format(
            self.root, post["id"])
        ).json()["media_metadata"]["metadata"]

        ext = data["ZIP:ZipFileName"].rpartition(".")[2]
        print(post["id"], ext)
        fmt = ("{:>06}." + ext).format
        delays = data["Ugoira:FrameDelays"]
        return [{"file": fmt(index), "delay": delay}
                for index, delay in enumerate(delays)]


INSTANCES = {
    "danbooru": {
        "root": None,
        "pattern": r"(?:danbooru|hijiribe|sonohara|safebooru)\.donmai\.us",
    },
    "e621": {
        "root": None,
        "pattern": r"e(?:621|926)\.net",
        "headers": {"User-Agent": "gallery-dl/{} (by mikf)".format(
            __version__)},
        "pools": "sort",
        "popular": "/popular.json",
        "page-limit": 750,
        "per-page": 320,
        "request-interval-min": 1.0,
    },
    "atfbooru": {
        "root": "https://booru.allthefallen.moe",
        "pattern": r"booru\.allthefallen\.moe",
        "page-limit": 5000,
    },
}

BASE_PATTERN = DanbooruExtractor.update(INSTANCES)


class DanbooruTagExtractor(DanbooruExtractor):
    """Extractor for danbooru posts from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/posts\?(?:[^&#]*&)*tags=([^&#]*)"
    test = (
        ("https://danbooru.donmai.us/posts?tags=bonocho", {
            "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
        }),
        # test page transitions
        ("https://danbooru.donmai.us/posts?tags=mushishi", {
            "count": ">= 300",
        }),
        # 'external' option (#1747)
        ("https://danbooru.donmai.us/posts?tags=pixiv_id%3A1476533", {
            "options": (("external", True),),
            "pattern": r"https://i\.pximg\.net/img-original/img"
                       r"/2008/08/28/02/35/48/1476533_p0\.jpg",
        }),
        ("https://e621.net/posts?tags=anry", {
            "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
            "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
        }),
        ("https://booru.allthefallen.moe/posts?tags=yume_shokunin", {
            "count": 12,
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho"),
        ("https://sonohara.donmai.us/posts?tags=bonocho"),
        ("https://safebooru.donmai.us/posts?tags=bonocho"),
        ("https://e926.net/posts?tags=anry"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        return self._pagination("/posts.json", {"tags": self.tags})


class DanbooruPoolExtractor(DanbooruExtractor):
    """Extractor for posts from danbooru pools"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name]}")
    archive_fmt = "p_{pool[id]}_{id}"
    pattern = BASE_PATTERN + r"/pool(?:s|/show)/(\d+)"
    test = (
        ("https://danbooru.donmai.us/pools/7659", {
            "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
        }),
        ("https://e621.net/pools/73", {
            "url": "1bd09a72715286a79eea3b7f09f51b3493eb579a",
            "content": "91abe5d5334425d9787811d7f06d34c77974cd22",
        }),
        ("https://booru.allthefallen.moe/pools/9", {
            "url": "902549ffcdb00fe033c3f63e12bc3cb95c5fd8d5",
            "count": 6,
        }),
        ("https://danbooru.donmai.us/pool/show/7659"),
        ("https://e621.net/pool/show/73"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)
        self.post_ids = ()

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        pool["name"] = pool["name"].replace("_", " ")
        self.post_ids = pool.pop("post_ids", ())
        return {"pool": pool}

    def posts(self):
        if self._pools == "sort":
            self.log.info("Fetching posts of pool %s", self.pool_id)

            id_to_post = {
                post["id"]: post
                for post in self._pagination(
                    "/posts.json", {"tags": "pool:" + self.pool_id})
            }

            posts = []
            append = posts.append
            for num, pid in enumerate(self.post_ids, 1):
                if pid in id_to_post:
                    post = id_to_post[pid]
                    post["num"] = num
                    append(post)
                else:
                    self.log.warning("Post %s is unavailable", pid)
            return posts

        else:
            params = {"tags": "pool:" + self.pool_id}
            return self._pagination("/posts.json", params)


class DanbooruPostExtractor(DanbooruExtractor):
    """Extractor for single danbooru posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post(?:s|/show)/(\d+)"
    test = (
        ("https://danbooru.donmai.us/posts/294929", {
            "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
        }),
        ("https://danbooru.donmai.us/posts/3613024", {
            "pattern": r"https?://.+\.zip$",
            "options": (("ugoira", True),)
        }),
        ("https://e621.net/posts/535", {
            "url": "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
            "content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
        }),
        ("https://booru.allthefallen.moe/posts/22", {
            "content": "21dda68e1d7e0a554078e62923f537d8e895cac8",
        }),
        ("https://danbooru.donmai.us/post/show/294929"),
        ("https://e621.net/post/show/535"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        post = self.request(url).json()
        return (post["post"] if "post" in post else post,)


class DanbooruPopularExtractor(DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + r"/(?:explore/posts/)?popular(?:\?([^#]*))?"
    test = (
        ("https://danbooru.donmai.us/explore/posts/popular"),
        (("https://danbooru.donmai.us/explore/posts/popular"
          "?date=2013-06-06&scale=week"), {
            "range": "1-120",
            "count": 120,
        }),
        ("https://e621.net/popular"),
        (("https://e621.net/explore/posts/popular"
          "?date=2019-06-01&scale=month"), {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": ">= 70",
        }),
        ("https://booru.allthefallen.moe/explore/posts/popular"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.params = match.group(match.lastindex)

    def metadata(self):
        self.params = params = text.parse_query(self.params)
        scale = params.get("scale", "day")
        date = params.get("date") or datetime.date.today().isoformat()

        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        if self.page_start is None:
            self.page_start = 1
        return self._pagination(self._popular_endpoint, self.params, True)


class DanbooruFavoriteExtractor(DanbooruExtractor):
    """Extractor for e621 favorites"""
    subcategory = "favorite"
    directory_fmt = ("{category}", "Favorites", "{user_id}")
    archive_fmt = "f_{user_id}_{id}"
    pattern = BASE_PATTERN + r"/favorites(?:\?([^#]*))?"
    test = (
        ("https://e621.net/favorites"),
        ("https://e621.net/favorites?page=2&user_id=53275", {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": "> 260",
        }),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.query = text.parse_query(match.group(match.lastindex))

    def metadata(self):
        return {"user_id": self.query.get("user_id", "")}

    def posts(self):
        if self.page_start is None:
            self.page_start = 1
        return self._pagination("/favorites.json", self.query, True)
