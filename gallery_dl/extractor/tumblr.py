# -*- coding: utf-8 -*-

# Copyright 2016-2017 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text, exception
from ..cache import memcache


class TumblrExtractor(Extractor):
    """Base class for tumblr extractors"""
    category = "tumblr"
    directory_fmt = ["{category}", "{name}"]
    filename_fmt = "{category}_{blog[name]}_{id}{offset}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)
        self.api = TumblrAPI(self, "photo")

    def items(self):
        blog = self.api.info(self.user)
        yield Message.Version, 1
        yield Message.Directory, blog

        for post in self.posts():
            if "photos" not in post:
                continue
            photos = post["photos"]
            del post["photos"]
            del post["trail"]
            for offset, photo in enumerate(photos, 1):
                photo.update(photo["original_size"])
                del photo["original_size"]
                del photo["alt_sizes"]
                post["extension"] = photo["url"].rpartition(".")[2]
                post["offset"] = "o{}".format(offset)
                post["photo"] = photo
                post["blog"] = blog
                yield Message.Url, photo["url"], post

    def posts(self):
        """Return an iterable containing all relevant posts"""


class TumblrUserExtractor(TumblrExtractor):
    """Extractor for all images from a tumblr-user"""
    subcategory = "user"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com(?:/page/\d+)?/?$"]
    test = [("http://demo.tumblr.com/", {
        "pattern": r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg",
        "count": 1,
    })]

    def posts(self):
        return self.api.posts(self.user, {})


class TumblrPostExtractor(TumblrExtractor):
    """Extractor for images from a single post on tumblr"""
    subcategory = "post"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com/post/(\d+)"]
    test = [("http://demo.tumblr.com/post/459265350", {
        "pattern": r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg",
        "count": 1,
    })]

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.post_id = match.group(2)

    def posts(self):
        return self.api.posts(self.user, {"id": self.post_id})


class TumblrTagExtractor(TumblrExtractor):
    """Extractor for images from a tumblr-user by tag"""
    subcategory = "tag"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com/tagged/(.+)"]
    test = [("http://demo.tumblr.com/tagged/Times%20Square", {
        "pattern": r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg",
        "count": 1,
    })]

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.tag = text.unquote(match.group(2))

    def posts(self):
        return self.api.posts(self.user, {"tag": self.tag})


class TumblrAPI():
    """Minimal interface for the Tumblr API v2"""
    API_KEY = "O3hU2tMi5e4Qs5t3vezEi6L0qRORJ5y9oUpSGsrWu8iA3UCc3B"

    def __init__(self, extractor, typ=None):
        self.api_key = extractor.config("api-key", TumblrAPI.API_KEY)
        self.params = {"offset": 0, "limit": 50, "type": typ}
        self.extractor = extractor

    @memcache(keyarg=1)
    def info(self, blog):
        """Return general information about a blog"""
        return self._call(blog, "info", {})["blog"]

    def posts(self, blog, params):
        """Retrieve published posts"""
        params.update(self.params)
        return self._pagination(blog, "posts", params)

    def _call(self, blog, endpoint, params):
        params["api_key"] = self.api_key
        url = "https://api.tumblr.com/v2/blog/{}.tumblr.com/{}".format(
            blog, endpoint)

        response = self.extractor.request(
            url, params=params, fatal=False).json()
        if response["meta"]["status"] == 404:
            raise exception.NotFoundError("user")
        elif response["meta"]["status"] != 200:
            self.extractor.log.error(response)
            raise exception.StopExtraction()

        return response["response"]

    def _pagination(self, blog, endpoint, params):
        while True:
            data = self._call(blog, endpoint, params)
            yield from data["posts"]
            params["offset"] += params["limit"]
            if params["offset"] >= data["total_posts"]:
                return
