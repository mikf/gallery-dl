# -*- coding: utf-8 -*-

# Copyright 2014-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/ and other Danbooru instances"""

from .common import BaseExtractor, Message
from .. import text, util
import datetime


class DanbooruExtractor(BaseExtractor):
    """Base class for danbooru extractors"""
    basecategory = "Danbooru"
    filename_fmt = "{category}_{id}_{filename}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 200
    request_interval = 1.0

    def _init(self):
        self.ugoira = self.config("ugoira", False)
        self.external = self.config("external", False)
        self.includes = False

        threshold = self.config("threshold")
        if isinstance(threshold, int):
            self.threshold = 1 if threshold < 1 else threshold
        else:
            self.threshold = self.per_page

        username, api_key = self._get_auth_info()
        if username:
            self.log.debug("Using HTTP Basic Auth for user '%s'", username)
            self.session.auth = (username, api_key)

    def skip(self, num):
        pages = num // self.per_page
        if pages >= self.page_limit:
            pages = self.page_limit - 1
        self.page_start = pages + 1
        return pages * self.per_page

    def items(self):
        self.session.headers["User-Agent"] = util.USERAGENT

        includes = self.config("metadata")
        if includes:
            if isinstance(includes, (list, tuple)):
                includes = ",".join(includes)
            elif not isinstance(includes, str):
                includes = "artist_commentary,children,notes,parent,uploader"
            self.includes = includes + ",id"

        data = self.metadata()
        for post in self.posts():

            try:
                url = post["file_url"]
            except KeyError:
                if self.external and post["source"]:
                    post.update(data)
                    yield Message.Directory, post
                    yield Message.Queue, post["source"], post
                continue

            text.nameext_from_url(url, post)
            post["date"] = text.parse_datetime(
                post["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")

            if post["extension"] == "zip":
                if self.ugoira:
                    post["frames"] = self._ugoira_frames(post)
                    post["_http_adjust_extension"] = False
                else:
                    url = post["large_file_url"]
                    post["extension"] = "webm"

            if url[0] == "/":
                url = self.root + url

            post.update(data)
            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def _pagination(self, endpoint, params, prefix=None):
        url = self.root + endpoint
        params["limit"] = self.per_page
        params["page"] = self.page_start

        first = True
        while True:
            posts = self.request(url, params=params).json()
            if isinstance(posts, dict):
                posts = posts["posts"]

            if posts:
                if self.includes:
                    params_meta = {
                        "only" : self.includes,
                        "limit": len(posts),
                        "tags" : "id:" + ",".join(str(p["id"]) for p in posts),
                    }
                    data = {
                        meta["id"]: meta
                        for meta in self.request(
                            url, params=params_meta).json()
                    }
                    for post in posts:
                        post.update(data[post["id"]])

                if prefix == "a" and not first:
                    posts.reverse()

                yield from posts

            if len(posts) < self.threshold:
                return

            if prefix:
                params["page"] = "{}{}".format(prefix, posts[-1]["id"])
            elif params["page"]:
                params["page"] += 1
            else:
                params["page"] = 2
            first = False

    def _ugoira_frames(self, post):
        data = self.request("{}/posts/{}.json?only=media_metadata".format(
            self.root, post["id"])
        ).json()["media_metadata"]["metadata"]

        ext = data["ZIP:ZipFileName"].rpartition(".")[2]
        fmt = ("{:>06}." + ext).format
        delays = data["Ugoira:FrameDelays"]
        return [{"file": fmt(index), "delay": delay}
                for index, delay in enumerate(delays)]


BASE_PATTERN = DanbooruExtractor.update({
    "danbooru": {
        "root": None,
        "pattern": r"(?:danbooru|hijiribe|sonohara|safebooru)\.donmai\.us",
    },
    "atfbooru": {
        "root": "https://booru.allthefallen.moe",
        "pattern": r"booru\.allthefallen\.moe",
    },
    "aibooru": {
        "root": None,
        "pattern": r"(?:safe.)?aibooru\.online",
    },
    "booruvar": {
        "root": "https://booru.borvar.art",
        "pattern": r"booru\.borvar\.art",
    },
})


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
        ("https://booru.allthefallen.moe/posts?tags=yume_shokunin", {
            "count": 12,
        }),
        ("https://aibooru.online/posts?tags=center_frills&z=1", {
            "pattern": r"https://cdn\.aibooru\.online/original"
                       r"/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w+",
            "count": ">= 3",
        }),
        ("https://booru.borvar.art/posts?tags=chibi&z=1", {
            "pattern": r"https://booru\.borvar\.art/data/original"
                       r"/[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}\.\w+",
            "count": ">= 3",
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho"),
        ("https://sonohara.donmai.us/posts?tags=bonocho"),
        ("https://safebooru.donmai.us/posts?tags=bonocho"),
        ("https://safe.aibooru.online/posts?tags=center_frills"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        tags = match.group(match.lastindex)
        self.tags = text.unquote(tags.replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        prefix = "b"
        for tag in self.tags.split():
            if tag.startswith("order:"):
                if tag == "order:id" or tag == "order:id_asc":
                    prefix = "a"
                elif tag == "order:id_desc":
                    prefix = "b"
                else:
                    prefix = None
            elif tag.startswith(
                    ("id:", "md5", "ordfav:", "ordfavgroup:", "ordpool:")):
                prefix = None
                break

        return self._pagination("/posts.json", {"tags": self.tags}, prefix)


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
        ("https://booru.allthefallen.moe/pools/9", {
            "url": "902549ffcdb00fe033c3f63e12bc3cb95c5fd8d5",
            "count": 6,
        }),
        ("https://booru.borvar.art/pools/2", {
            "url": "77fa3559a3fc919f72611f4e3dd0f919d19d3e0d",
            "count": 4,
        }),
        ("https://aibooru.online/pools/1"),
        ("https://danbooru.donmai.us/pool/show/7659"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.pool_id = match.group(match.lastindex)

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        pool["name"] = pool["name"].replace("_", " ")
        self.post_ids = pool.pop("post_ids", ())
        return {"pool": pool}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination("/posts.json", params, "b")


class DanbooruPostExtractor(DanbooruExtractor):
    """Extractor for single danbooru posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post(?:s|/show)/(\d+)"
    test = (
        ("https://danbooru.donmai.us/posts/294929", {
            "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
            "keyword": {"date": "dt:2008-08-12 04:46:05"},
        }),
        ("https://danbooru.donmai.us/posts/3613024", {
            "pattern": r"https?://.+\.zip$",
            "options": (("ugoira", True),)
        }),
        ("https://booru.allthefallen.moe/posts/22", {
            "content": "21dda68e1d7e0a554078e62923f537d8e895cac8",
        }),
        ("https://aibooru.online/posts/1", {
            "content": "54d548743cd67799a62c77cbae97cfa0fec1b7e9",
        }),
        ("https://booru.borvar.art/posts/1487", {
            "content": "91273ac1ea413a12be468841e2b5804656a50bff",
        }),
        ("https://danbooru.donmai.us/post/show/294929"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.post_id = match.group(match.lastindex)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        post = self.request(url).json()
        if self.includes:
            params = {"only": self.includes}
            post.update(self.request(url, params=params).json())
        return (post,)


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
        ("https://booru.allthefallen.moe/explore/posts/popular"),
        ("https://aibooru.online/explore/posts/popular"),
        ("https://booru.borvar.art/explore/posts/popular"),
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
        return self._pagination("/explore/posts/popular.json", self.params)
