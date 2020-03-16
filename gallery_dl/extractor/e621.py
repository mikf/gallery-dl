# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://e621.net/"""

from .common import Extractor, Message, SharedConfigMixin
from .. import text
import datetime
import time


BASE_PATTERN = r"(?:https?://)?e(621|926)\.net"


class E621Extractor(SharedConfigMixin, Extractor):
    """Base class for e621 extractors"""
    basecategory = "booru"
    category = "e621"
    filename_fmt = "{category}_{id}_{file[md5]}.{extension}"
    page_limit = 750
    page_start = None
    per_page = 320
    _last_request = 0

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = "https://e{}.net".format(match.group(1))
        self.params = {}

        username, api_key = self._get_auth_info()
        if username:
            self.log.debug("Using HTTP Basic Auth for user '%s'", username)
            self.session.auth = (username, api_key)

    def request(self, url, **kwargs):
        diff = time.time() - E621Extractor._last_request
        if diff < 1.0:
            self.log.debug("Sleeping for %s seconds", diff)
            time.sleep(diff)
        kwargs["headers"] = {"User-Agent": "gallery-dl/1.13.0 (by mikf)"}
        response = Extractor.request(self, url, **kwargs)
        E621Extractor._last_request = time.time()
        return response

    def items(self):
        data = self.metadata()
        for post in self.posts():
            file = post["file"]

            if not file["url"]:
                ihash = file["md5"]
                file["url"] = "https://static1.{}/data/{}/{}/{}.{}".format(
                    self.root[8:], ihash[0:2], ihash[2:4], ihash, file["ext"])

            post["filename"] = file["md5"]
            post["extension"] = file["ext"]
            post.update(data)
            yield Message.Directory, post
            yield Message.Url, file["url"], post

    def metadata(self):
        return {}

    def posts(self):
        return self._pagination(self.root + "/posts.json")

    def _pagination(self, url):
        params = self.params.copy()
        params["limit"] = self.per_page
        tags = params.get("tags", "")

        while True:
            posts = self.request(url, params=params).json()["posts"]
            yield from posts

            if len(posts) < self.per_page:
                return
            params["tags"] = "id:<{} {}".format(posts[-1]["id"], tags)


class E621TagExtractor(E621Extractor):
    """Extractor for e621 posts from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/posts?(?:\?.*?tags=|/index/\d+/)([^&#]+)"
    test = (
        ("https://e621.net/posts?tags=anry", {
            "url": "8021e5ea28d47c474c1ffc9bd44863c4d45700ba",
            "content": "501d1e5d922da20ee8ff9806f5ed3ce3a684fd58",
        }),
        ("https://e926.net/posts?tags=anry"),
        ("https://e621.net/post/index/1/anry"),
        ("https://e621.net/post?tags=anry"),
    )

    def __init__(self, match):
        E621Extractor.__init__(self, match)
        self.params["tags"] = text.unquote(match.group(2).replace("+", " "))

    def metadata(self):
        return {"search_tags": self.params["tags"]}


class E621PoolExtractor(E621Extractor):
    """Extractor for e621 pools"""
    subcategory = "pool"
    directory_fmt = ("{category}", "pool", "{pool[id]} {pool[name]}")
    archive_fmt = "p_{pool[id]}_{id}"
    pattern = BASE_PATTERN + r"/pool(?:s|/show)/(\d+)"
    test = (
        ("https://e621.net/pools/73", {
            "url": "842f2fb065c7c339486a9b1d689020b8569888ed",
            "content": "c2c87b7a9150509496cddc75ccab08109922876a",
        }),
        ("https://e621.net/pool/show/73"),
    )

    def __init__(self, match):
        E621Extractor.__init__(self, match)
        self.pool_id = match.group(2)
        self.params["tags"] = "pool:" + self.pool_id

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        pool["name"] = pool["name"].replace("_", " ")
        del pool["post_ids"]
        return {"pool": pool}


class E621PostExtractor(E621Extractor):
    """Extractor for single e621 posts"""
    subcategory = "post"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/post(?:s|/show)/(\d+)"
    test = (
        ("https://e621.net/posts/535", {
            "url": "f7f78b44c9b88f8f09caac080adc8d6d9fdaa529",
            "content": "66f46e96a893fba8e694c4e049b23c2acc9af462",
        }),
        ("https://e621.net/post/show/535"),
    )

    def __init__(self, match):
        E621Extractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        return (self.request(url).json()["post"],)


class E621PopularExtractor(E621Extractor):
    """Extractor for popular images from e621"""
    subcategory = "popular"
    directory_fmt = ("{category}", "popular", "{scale}", "{date}")
    archive_fmt = "P_{scale[0]}_{date}_{id}"
    pattern = BASE_PATTERN + r"/explore/posts/popular(?:\?([^#]*))?"
    test = (
        ("https://e621.net/explore/posts/popular"),
        (("https://e621.net/explore/posts/popular"
          "?date=2019-06-01&scale=month"), {
            "pattern": r"https://static\d.e621.net/data/../../[0-9a-f]+",
            "count": ">= 70",
        })
    )

    def __init__(self, match):
        E621Extractor.__init__(self, match)
        self.params.update(text.parse_query(match.group(2)))

    def metadata(self):
        scale = self.params.get("scale", "day")
        date = self.params.get("date") or datetime.date.today().isoformat()
        date = date[:10]

        if scale == "week":
            date = datetime.date.fromisoformat(date)
            date = (date - datetime.timedelta(days=date.weekday())).isoformat()
        elif scale == "month":
            date = date[:-3]

        return {"date": date, "scale": scale}

    def posts(self):
        url = self.root + "/explore/posts/popular.json"
        return self._pagination(url)
