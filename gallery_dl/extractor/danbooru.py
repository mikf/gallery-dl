# -*- coding: utf-8 -*-

# Copyright 2014-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://danbooru.donmai.us/"""

from .common import Extractor, Message, SharedConfigMixin
from .. import text


BASE_PATTERN = (
    r"(?:https?://)?"
    r"(danbooru|hijiribe|sonohara|safebooru)"
    r"\.donmai\.us"
)


class DanbooruExtractor(SharedConfigMixin, Extractor):
    """Base class for danbooru extractors"""
    basecategory = "booru"
    category = "danbooru"
    filename_fmt = "{category}_{id}_{md5}.{extension}"
    page_limit = 1000
    page_start = None
    per_page = 100

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.root = "https://{}.donmai.us".format(match.group(1))
        self.api_url = self.root + "/posts.json"
        self.ugoira = self.config("ugoira", True)
        self.params = {}

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
        return {}

    def posts(self):
        params = self.params.copy()
        params["limit"] = self.per_page
        params["page"] = self.page_start

        while True:
            posts = self.request(self.api_url, params=params).json()
            yield from posts

            if len(posts) < self.per_page:
                return
            params["page"] = "b{}".format(posts[-1]["id"])


class DanbooruTagExtractor(DanbooruExtractor):
    """Extractor for danbooru posts from tag searches"""
    subcategory = "tag"
    directory_fmt = ("{category}", "{search_tags}")
    archive_fmt = "t_{search_tags}_{id}"
    pattern = BASE_PATTERN + r"/posts\?(?:[^&#]*&)*tags=(?P<tags>[^&#]+)"
    test = (
        ("https://danbooru.donmai.us/posts?tags=bonocho", {
            "content": "b196fb9f1668109d7774a0a82efea3ffdda07746",
        }),
        # test page transitions
        ("https://danbooru.donmai.us/posts?tags=canvas_%28cocktail_soft%29", {
            "count": ">= 50",
        }),
        ("https://hijiribe.donmai.us/posts?tags=bonocho"),
        ("https://sonohara.donmai.us/posts?tags=bonocho"),
        ("https://safebooru.donmai.us/posts?tags=bonocho"),
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.params["tags"] = text.unquote(match.group(2).replace("+", " "))

    def metadata(self):
        return {"search_tags": self.params["tags"]}


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
        DanbooruExtractor.__init__(self, match)
        self.pool_id = match.group(2)
        self.params["tags"] = "pool:" + self.pool_id

    def metadata(self):
        url = "{}/pools/{}.json".format(self.root, self.pool_id)
        pool = self.request(url).json()
        del pool["post_ids"]
        return {"pool": pool}


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
            "pattern": r"https?://.+\.webm$",
            "options": (("ugoira", False),)
        })
    )

    def __init__(self, match):
        DanbooruExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        url = "{}/posts/{}.json".format(self.root, self.post_id)
        return (self.request(url).json(),)


r'''
class DanbooruPopularExtractor(booru.PopularMixin, DanbooruExtractor):
    """Extractor for popular images from danbooru"""
    pattern = BASE_PATTERN + r"/explore/posts/popular(?:\?(?P<query>[^#]*))?"
    test = (
        ("https://danbooru.donmai.us/explore/posts/popular"),
        (("https://danbooru.donmai.us/explore/posts/popular"
          "?date=2013-06-06+03%3A34%3A22+-0400&scale=week"), {
            "count": ">= 1",
        }),
    )

    def __init__(self, match):
        super().__init__(match)
        urlfmt = "{scheme}://{subdomain}.donmai.us/explore/posts/popular.json"
        self.api_url = urlfmt.format(
            scheme=self.scheme, subdomain=self.subdomain)
'''
