# -*- coding: utf-8 -*-

# Copyright 2016-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text, oauth, exception
from datetime import datetime, timedelta
import re


def _original_inline_image(url):
    return re.sub(
        (r"https?://(\d+\.media\.tumblr\.com(?:/[0-9a-f]+)?"
         r"/tumblr(?:_inline)?_[^_]+)_\d+\.([0-9a-z]+)"),
        r"https://\1_1280.\2", url
    )


def _original_video(url):
    return re.sub(
        (r"https?://((?:vt|vtt|ve)(?:\.media)?\.tumblr\.com"
         r"/tumblr_[^_]+)_\d+\.([0-9a-z]+)"),
        r"https://\1.\2", url
    )


POST_TYPES = frozenset((
    "text", "quote", "link", "answer", "video", "audio", "photo", "chat"))

BASE_PATTERN = (
    r"(?:tumblr:(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+\.tumblr\.com))")


class TumblrExtractor(Extractor):
    """Base class for tumblr extractors"""
    category = "tumblr"
    directory_fmt = ("{category}", "{blog_name}")
    filename_fmt = "{category}_{blog_name}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    cookiedomain = None

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.blog = match.group(1) or match.group(2)
        self.api = TumblrAPI(self)

        self.types = self._setup_posttypes()
        self.avatar = self.config("avatar", False)
        self.inline = self.config("inline", True)
        self.reblogs = self.config("reblogs", True)
        self.external = self.config("external", False)

        if len(self.types) == 1:
            self.api.posts_type = next(iter(self.types))
        elif not self.types:
            self.log.warning("no valid post types selected")

        if self.reblogs == "same-blog":
            self._skip_reblog = self._skip_reblog_same_blog

        self.date_min, self.api.before = self._get_date_min_max(0, None)

    def items(self):
        blog = None

        for post in self.posts():
            if self.date_min > post["timestamp"]:
                return
            if post["type"] not in self.types:
                continue
            if not blog:
                blog = self.api.info(self.blog)
                blog["uuid"] = self.blog

                if self.avatar:
                    url = self.api.avatar(self.blog)
                    yield Message.Directory, {"blog": blog}
                    yield self._prepare_avatar(url, post.copy(), blog)

            reblog = "reblogged_from_id" in post
            if reblog and self._skip_reblog(post):
                continue
            post["reblogged"] = reblog

            if "trail" in post:
                del post["trail"]
            post["blog"] = blog
            post["date"] = text.parse_timestamp(post["timestamp"])
            yield Message.Directory, post
            post["num"] = 0

            if "photos" in post:  # type "photo" or "link"
                photos = post["photos"]
                del post["photos"]

                for photo in photos:
                    post["photo"] = photo
                    photo.update(photo["original_size"])
                    del photo["original_size"]
                    del photo["alt_sizes"]
                    yield self._prepare_image(photo["url"], post)

            url = post.get("audio_url")  # type "audio"
            if url and url.startswith("https://a.tumblr.com/"):
                yield self._prepare(url, post)

            url = post.get("video_url")  # type "video"
            if url:
                yield self._prepare(_original_video(url), post)

            if self.inline and "reblog" in post:  # inline media
                # only "chat" posts are missing a "reblog" key in their
                # API response, but they can't contain images/videos anyway
                body = post["reblog"]["comment"] + post["reblog"]["tree_html"]
                for url in re.findall('<img src="([^"]+)"', body):
                    url = _original_inline_image(url)
                    yield self._prepare_image(url, post)
                for url in re.findall('<source src="([^"]+)"', body):
                    url = _original_video(url)
                    yield self._prepare(url, post)

            if self.external:  # external links
                post["extension"] = None
                url = post.get("permalink_url") or post.get("url")
                if url:
                    yield Message.Queue, url, post

    def posts(self):
        """Return an iterable containing all relevant posts"""

    def _setup_posttypes(self):
        types = self.config("posts", "all")

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
                self.log.warning("Invalid post types: '%s'",
                                 "', '".join(sorted(invalid)))
            return types

    @staticmethod
    def _prepare(url, post):
        text.nameext_from_url(url, post)
        post["num"] += 1
        post["hash"] = post["filename"].partition("_")[2]
        return Message.Url, url, post

    @staticmethod
    def _prepare_image(url, post):
        text.nameext_from_url(url, post)
        post["num"] += 1

        parts = post["filename"].split("_")
        try:
            post["hash"] = parts[1] if parts[1] != "inline" else parts[2]
        except IndexError:
            # filename doesn't follow the usual pattern (#129)
            post["hash"] = post["filename"]

        return Message.Url, url, post

    @staticmethod
    def _prepare_avatar(url, post, blog):
        text.nameext_from_url(url, post)
        post["num"] = 1
        post["blog"] = blog
        post["reblogged"] = False
        post["type"] = post["id"] = post["hash"] = "avatar"
        return Message.Url, url, post

    def _skip_reblog(self, _):
        return not self.reblogs

    def _skip_reblog_same_blog(self, post):
        return self.blog != post.get("reblogged_root_uuid")


class TumblrUserExtractor(TumblrExtractor):
    """Extractor for all images from a tumblr-user"""
    subcategory = "user"
    pattern = BASE_PATTERN + r"(?:/page/\d+|/archive)?/?$"
    test = (
        ("http://demo.tumblr.com/", {
            "pattern": r"https://\d+\.media\.tumblr\.com"
                       r"/tumblr_[^/_]+_\d+\.jpg",
            "count": 1,
            "options": (("posts", "photo"),),
        }),
        ("http://demo.tumblr.com/", {
            "pattern": (r"https?://(?:$|"
                        r"\d+\.media\.tumblr\.com/.+_1280\.jpg|"
                        r"a\.tumblr\.com/tumblr_\w+)"),
            "count": 3,
            "options": (("posts", "all"), ("external", True))
        }),
        ("https://mikf123-hidden.tumblr.com/", {  # dashbord-only
            "count": 2,
            "keyword": {"tags": ["test", "hidden"]},
        }),
        ("https://mikf123-private.tumblr.com/", {  # password protected
            "count": 2,
            "keyword": {"tags": ["test", "private"]},
        }),
        ("https://mikf123-private-hidden.tumblr.com/", {  # both
            "count": 2,
            "keyword": {"tags": ["test", "private", "hidden"]},
        }),
        ("https://mikf123.tumblr.com/", {  # date-min/-max/-format (#337)
            "count": 4,
            "options": (("date-min", "201804"), ("date-max", "201805"),
                        ("date-format", "%Y%m"))
        }),
        ("https://demo.tumblr.com/page/2"),
        ("https://demo.tumblr.com/archive"),
        ("tumblr:http://www.b-authentique.com/"),
        ("tumblr:www.b-authentique.com"),
    )

    def posts(self):
        return self.api.posts(self.blog, {})


class TumblrPostExtractor(TumblrExtractor):
    """Extractor for images from a single post on tumblr"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:post|image)/(\d+)"
    test = (
        ("http://demo.tumblr.com/post/459265350", {
            "pattern": (r"https://\d+\.media\.tumblr\.com"
                        r"/tumblr_[^/_]+_1280.jpg"),
            "count": 1,
        }),
        ("https://mikf123.tumblr.com/post/167770226574/text-post", {
            "count": 2,
        }),
        ("https://mikf123.tumblr.com/post/181022561719/quote-post", {
            "count": 1,
        }),
        ("https://mikf123.tumblr.com/post/167623351559/link-post", {
            "count": 2,
        }),
        ("https://mikf123.tumblr.com/post/167633596145/video-post", {
            "count": 2,
        }),
        ("https://mikf123.tumblr.com/post/167770026604/audio-post", {
            "count": 2,
        }),
        ("https://mikf123.tumblr.com/post/172687798174/photo-post", {
            "count": 4,
        }),
        ("https://mikf123.tumblr.com/post/181022380064/chat-post", {
            "count": 0,
        }),
        ("http://ziemniax.tumblr.com/post/109697912859/", {
            "exception": exception.NotFoundError,  # HTML response (#297)
        }),
        ("http://demo.tumblr.com/image/459265350"),
    )

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.post_id = match.group(3)
        self.reblogs = True
        self.date_min = 0

    def posts(self):
        return self.api.posts(self.blog, {"id": self.post_id})

    @staticmethod
    def _setup_posttypes():
        return POST_TYPES


class TumblrTagExtractor(TumblrExtractor):
    """Extractor for images from a tumblr-user by tag"""
    subcategory = "tag"
    pattern = BASE_PATTERN + r"/tagged/([^/?#]+)"
    test = ("http://demo.tumblr.com/tagged/Times%20Square", {
        "pattern": (r"https://\d+\.media\.tumblr\.com/tumblr_[^/_]+_1280.jpg"),
        "count": 1,
    })

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.tag = text.unquote(match.group(3).replace("-", " "))

    def posts(self):
        return self.api.posts(self.blog, {"tag": self.tag})


class TumblrLikesExtractor(TumblrExtractor):
    """Extractor for images from a tumblr-user's liked posts"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{blog_name}", "likes")
    archive_fmt = "f_{blog[name]}_{id}_{num}"
    pattern = BASE_PATTERN + r"/likes"
    test = ("http://mikf123.tumblr.com/likes", {
        "count": 1,
    })

    def posts(self):
        return self.api.likes(self.blog)


class TumblrAPI(oauth.OAuth1API):
    """Minimal interface for the Tumblr API v2"""
    API_KEY = "O3hU2tMi5e4Qs5t3vezEi6L0qRORJ5y9oUpSGsrWu8iA3UCc3B"
    API_SECRET = "sFdsK3PDdP2QpYMRAoq0oDnw0sFS24XigXmdfnaeNZpJpqAn03"
    BLOG_CACHE = {}

    def __init__(self, extractor):
        oauth.OAuth1API.__init__(self, extractor)
        self.posts_type = self.before = None

    def info(self, blog):
        """Return general information about a blog"""
        if blog not in self.BLOG_CACHE:
            self.BLOG_CACHE[blog] = self._call(blog, "info", {})["blog"]
        return self.BLOG_CACHE[blog]

    def avatar(self, blog, size="512"):
        """Retrieve a blog avatar"""
        if self.api_key:
            url_fmt = "https://api.tumblr.com/v2/blog/{}/avatar/{}?api_key={}"
            return url_fmt.format(blog, size, self.api_key)
        params = {"size": size}
        data = self._call(blog, "avatar", params, allow_redirects=False)
        return data["avatar_url"]

    def posts(self, blog, params):
        """Retrieve published posts"""
        params.update({"offset": 0, "limit": 50, "reblog_info": "true"})
        if self.posts_type:
            params["type"] = self.posts_type
        if self.before:
            params["before"] = self.before
        while True:
            data = self._call(blog, "posts", params)
            self.BLOG_CACHE[blog] = data["blog"]
            yield from data["posts"]
            params["offset"] += params["limit"]
            if params["offset"] >= data["total_posts"]:
                return

    def likes(self, blog):
        """Retrieve liked posts"""
        params = {"limit": "50", "before": self.before}
        while True:
            posts = self._call(blog, "likes", params)["liked_posts"]
            if not posts:
                return
            yield from posts
            params["before"] = posts[-1]["liked_timestamp"]

    def _call(self, blog, endpoint, params, **kwargs):
        if self.api_key:
            params["api_key"] = self.api_key
        url = "https://api.tumblr.com/v2/blog/{}/{}".format(
            blog, endpoint)

        response = self.request(url, params=params, **kwargs)

        try:
            data = response.json()
        except ValueError:
            data = response.text
            status = response.status_code
        else:
            status = data["meta"]["status"]
            if 200 <= status < 400:
                return data["response"]

        if status == 403:
            raise exception.AuthorizationError()
        elif status == 404:
            raise exception.NotFoundError("user or post")
        elif status == 429:

            # daily rate limit
            if response.headers.get("x-ratelimit-perday-remaining") == "0":
                reset = response.headers.get("x-ratelimit-perday-reset")
                t = (datetime.now() + timedelta(seconds=float(reset))).time()

                self.log.error("Daily API rate limit exceeded")
                raise exception.StopExtraction(
                    "Aborting - Rate limit will reset at %s",
                    "{:02}:{:02}:{:02}".format(t.hour, t.minute, t.second))

            # hourly rate limit
            reset = response.headers.get("x-ratelimit-perhour-reset")
            if reset:
                self.log.info("Hourly API rate limit exceeded")
                self.extractor.wait(seconds=reset)
                return self._call(blog, endpoint, params)

        raise exception.StopExtraction(data)
