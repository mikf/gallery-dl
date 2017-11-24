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
import re


def _original_image(url):
    if url.endswith(".gif") and "_inline_" in url:
        return url
    return re.sub(
        (r"https?://\d+\.media\.tumblr\.com"
         r"/([0-9a-f]+)/tumblr_([^/?&#.]+)_\d+\.([0-9a-z]+)"),
        r"http://data.tumblr.com/\1/tumblr_\2_raw.\3", url
    )


def _original_video(url):
    return re.sub(
        (r"https?://vt\.media\.tumblr\.com"
         r"/tumblr_([^_]+)_\d+\.([0-9a-z]+)"),
        r"https://vt.media.tumblr.com/tumblr_\1.\2", url
    )


POST_TYPES = frozenset((
    "text", "quote", "link", "answer", "video", "audio", "photo", "chat"))


class TumblrExtractor(Extractor):
    """Base class for tumblr extractors"""
    category = "tumblr"
    directory_fmt = ["{category}", "{name}"]
    filename_fmt = "{category}_{blog[name]}_{id}{offset:?o//}.{extension}"

    def __init__(self, match):
        Extractor.__init__(self)
        self.user = match.group(1)
        self.api = TumblrAPI(self)

        self.types = self._setup_posttypes()
        self.inline = self.config("inline", False)
        self.external = self.config("external", False)

        if len(self.types) == 1:
            self.api.params["type"] = next(iter(self.types))
        elif not self.types:
            self.log.warning("no valid post types selected")

    def items(self):
        blog = self.api.info(self.user)
        yield Message.Version, 1
        yield Message.Directory, blog

        for post in self.posts():
            if post["type"] not in self.types:
                continue

            post["blog"] = blog
            post["offset"] = 0

            if "trail" in post:
                del post["trail"]

            if "photos" in post:  # type "photo" or "link"
                photos = post["photos"]
                del post["photos"]

                for photo in photos:
                    post["photo"] = photo
                    photo.update(photo["original_size"])
                    del photo["original_size"]
                    del photo["alt_sizes"]
                    yield self._prepare(_original_image(photo["url"]), post)

            if "audio_url" in post:  # type: "audio"
                yield self._prepare(post["audio_url"], post)

            if "video_url" in post:  # type: "video"
                yield self._prepare(_original_video(post["video_url"]), post)

            if self.inline:  # inline images
                for key in ("body", "description"):
                    if key in post:
                        for url in re.findall('<img src="([^"]+)"', post[key]):
                            yield self._prepare(_original_image(url), post)

            if self.external:  # external links
                post["extension"] = None
                for key in ("permalink_url", "url"):
                    if key in post:
                        yield Message.Queue, post[key], post

    def posts(self):
        """Return an iterable containing all relevant posts"""

    def _setup_posttypes(self):
        types = self.config("posts", ("photo",))

        if types == "all":
            return POST_TYPES

        elif not types:
            return frozenset()

        else:
            if isinstance(types, str):
                types = types.split(",")
            types = frozenset(types)

            invalid = types - POST_TYPES
            if invalid:
                types = types & POST_TYPES
                self.log.warning('invalid post types: "%s"',
                                 '", "'.join(sorted(invalid)))
            return types

    @staticmethod
    def _prepare(url, post):
        post["offset"] += 1
        return Message.Url, url, text.nameext_from_url(url, post)


class TumblrUserExtractor(TumblrExtractor):
    """Extractor for all images from a tumblr-user"""
    subcategory = "user"
    pattern = [r"(?:https?://)?([^.]+)\.tumblr\.com(?:/page/\d+)?/?$"]
    test = [
        ("http://demo.tumblr.com/", {
            "pattern": (r"https?://\d+\.media\.tumblr\.com"
                        r"/tumblr_[^/_]+_\d+\.jpg"),
            "count": 1,
        }),
        ("http://demo.tumblr.com/", {
            "pattern": (r"https?://(?:$|"
                        r"\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280\.jpg|"
                        r"w+\.tumblr\.com/audio_file/demo/\d+/tumblr_\w+)"),
            "count": 3,
            "options": (("posts", "all"), ("external", True), ("inline", True))
        }),
    ]

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

    @staticmethod
    def _setup_posttypes():
        return POST_TYPES


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

    def __init__(self, extractor):
        self.api_key = extractor.config("api-key", TumblrAPI.API_KEY)
        self.params = {"offset": 0, "limit": 50}
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
            raise exception.NotFoundError("user or post")
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
