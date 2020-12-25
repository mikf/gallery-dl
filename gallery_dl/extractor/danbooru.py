# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/"""

from .common import Extractor, Message
from .. import text
import datetime

BASE_PATTERN = (
    r"(?:https?://)?"
    r"(danbooru|hijiribe|sonohara|safebooru)"
    r"\.donmai\.us"
)


class DanbooruExtractor(Extractor):
    """Base class for danbooru extractors"""
    basecategory = "booru"
    category = "danbooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 200

    def __init__(self, match):
        super().__init__(match)
        self.root = "https://{}.donmai.us".format(match.group(1))
        self.ugoira = self.config("ugoira", False)

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
        data = self.metadata()
        for post in self.posts():
            try:
                url = post["file_url"]
            except KeyError:
                continue

            text.nameext_from_url(url, post)
            if post["extension"] == "zip":
                if self.ugoira:
                    post["frames"] = self.request(
                        "{}/posts/{}.json?only=pixiv_ugoira_frame_data".format(
                            self.root, post["id"])
                    ).json()["pixiv_ugoira_frame_data"]["data"]
                else:
                    url = post["large_file_url"]
                    post["extension"] = "webm"

            post.update(data)
            yield Message.Directory, post
            yield Message.Url, url, post

    def metadata(self):
        return ()

    def posts(self):
        return ()

    def _pagination(self, endpoint, params=None, pagenum=False):
        url = self.root + endpoint

        if params is None:
            params = {}
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


class DanbooruTagExtractor(DanbooruExtractor):
    """Extractor for danbooru posts from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/posts\?(?:[^&#]*&)*tags=([^&#]+)"
    test = (
        ("https://danbooru.donmai.us/posts?tags=bonocho", {
            "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
        }),
        # test page transitions
        ("https://danbooru.donmai.us/posts?tags=mushishi", {
            "count": ">= 300",
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho"),
        ("https://sonohara.donmai.us/posts?tags=bonocho"),
        ("https://safebooru.donmai.us/posts?tags=bonocho"),
    )

    def __init__(self, match):
        super().__init__(match)
        self.tags = text.unquote(match.group(2).replace("+", " "))

    def metadata(self):
        return {"search_tags": self.tags}

    def posts(self):
        params = {"tags": self.tags}
        return self._pagination("/posts.json", params)


class DanbooruPoolExtractor(DanbooruExtractor):
    """Extractor for posts from danbooru pools"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name]}")
    archive_fmt = "p_{pool[id]}_{id}"
    pattern = BASE_PATTERN + r"/pools/(\d+)"
    test = ("https://danbooru.donmai.us/pools/7659", {
        "content": "b16bab12bea5f7ea9e0a836bf8045f280e113d99",
    })

    def __init__(self, match):
        super().__init__(match)
        self.pool_id = match.group(2)
        self.post_ids = ()

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        pool["name"] = pool["name"].replace("_", " ")
        self.post_ids = pool.pop("post_ids")
        return {"pool": pool}

    def posts(self):
        params = {"tags": "pool:" + self.pool_id}
        return self._pagination("/posts.json", params)


class DanbooruPostExtractor(DanbooruExtractor):
    """Extractor for single danbooru posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/posts/(\d+)"
    test = (
        ("https://danbooru.donmai.us/posts/294929", {
            "content": "5e255713cbf0a8e0801dc423563c34d896bb9229",
        }),
        ("https://danbooru.donmai.us/posts/3613024", {
            "pattern": r"https?://.+\.zip$",
            "options": (("ugoira", True),)
        })
    )

    def __init__(self, match):
        super().__init__(match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        post = self.request(url).json()
        return (post["post"] if "post" in post else post,)


class DanbooruPopularExtractor(DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + r"/explore/posts/popular(?:\?([^#]*))?"
    test = (
        ("https://danbooru.donmai.us/explore/posts/popular"),
        (("https://danbooru.donmai.us/explore/posts/popular"
          "?date=2013-06-06&scale=week"), {
            "range": "1-120",
            "count": 120,
        }),
    )

    def __init__(self, match):
        super().__init__(match)
        self.params = text.parse_query(match.group(2))

    def metadata(self):
        scale = self.params.get("scale", "day")
        date = self.params.get("date") or datetime.date.today().isoformat()

        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        if self.page_start is None:
            self.page_start = 1
        return self._pagination(
            "/explore/posts/popular.json", self.params, True)
