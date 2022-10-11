# -*- coding: utf-8 -*-

# Copyright 2016-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text, oauth, exception
from datetime import datetime, timedelta
import re


BASE_PATTERN = (
    r"(?:tumblr:(?:https?://)?([^/]+)|"
    r"(?:https?://)?"
    r"(?:www\.tumblr\.com/(?:blog/(?:view/)?)?([\w-]+)|"
    r"([\w-]+\.tumblr\.com)))"
)

POST_TYPES = frozenset((
    "text", "quote", "link", "answer", "video", "audio", "photo", "chat"))


class TumblrExtractor(Extractor):
    """Base class for tumblr extractors"""
    category = "tumblr"
    directory_fmt = ("{category}", "{blog_name}")
    filename_fmt = "{category}_{blog_name}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"
    cookiedomain = None

    def __init__(self, match):
        Extractor.__init__(self, match)

        name = match.group(2)
        if name:
            self.blog = name + ".tumblr.com"
        else:
            self.blog = match.group(1) or match.group(3)

        self.api = TumblrAPI(self)
        self.types = self._setup_posttypes()
        self.avatar = self.config("avatar", False)
        self.inline = self.config("inline", True)
        self.reblogs = self.config("reblogs", True)
        self.external = self.config("external", False)
        self.original = self.config("original", True)

        if len(self.types) == 1:
            self.api.posts_type = next(iter(self.types))
        elif not self.types:
            self.log.warning("no valid post types selected")

        if self.reblogs == "same-blog":
            self._skip_reblog = self._skip_reblog_same_blog

        self.date_min, self.api.before = self._get_date_min_max(0, None)

    def items(self):
        blog = None

        # pre-compile regular expressions
        self._sub_video = re.compile(
            r"https?://((?:vt|vtt|ve)(?:\.media)?\.tumblr\.com"
            r"/tumblr_[^_]+)_\d+\.([0-9a-z]+)").sub
        if self.inline:
            self._sub_image = re.compile(
                r"https?://(\d+\.media\.tumblr\.com(?:/[0-9a-f]+)?"
                r"/tumblr(?:_inline)?_[^_]+)_\d+\.([0-9a-z]+)").sub
            self._subn_orig_image = re.compile(r"/s\d+x\d+/").subn
            _findall_image = re.compile('<img src="([^"]+)"').findall
            _findall_video = re.compile('<source src="([^"]+)"').findall

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
            posts = []

            if "photos" in post:  # type "photo" or "link"
                photos = post["photos"]
                del post["photos"]

                for photo in photos:
                    post["photo"] = photo

                    best_photo = photo["original_size"]
                    for alt_photo in photo["alt_sizes"]:
                        if (alt_photo["height"] > best_photo["height"] or
                                alt_photo["width"] > best_photo["width"]):
                            best_photo = alt_photo
                    photo.update(best_photo)

                    if self.original and "/s2048x3072/" in photo["url"] and (
                            photo["width"] == 2048 or photo["height"] == 3072):
                        photo["url"], fb = self._original_photo(photo["url"])
                        if fb:
                            post["_fallback"] = self._original_image_fallback(
                                photo["url"], post["id"])

                    del photo["original_size"]
                    del photo["alt_sizes"]
                    posts.append(
                        self._prepare_image(photo["url"], post.copy()))
                    del post["photo"]
                    post.pop("_fallback", None)

            url = post.get("audio_url")  # type "audio"
            if url and url.startswith("https://a.tumblr.com/"):
                posts.append(self._prepare(url, post.copy()))

            url = post.get("video_url")  # type "video"
            if url:
                posts.append(self._prepare(
                    self._original_video(url), post.copy()))

            if self.inline and "reblog" in post:  # inline media
                # only "chat" posts are missing a "reblog" key in their
                # API response, but they can't contain images/videos anyway
                body = post["reblog"]["comment"] + post["reblog"]["tree_html"]
                for url in _findall_image(body):
                    url, fb = self._original_inline_image(url)
                    if fb:
                        post["_fallback"] = self._original_image_fallback(
                            url, post["id"])
                    posts.append(self._prepare_image(url, post.copy()))
                    post.pop("_fallback", None)
                for url in _findall_video(body):
                    url = self._original_video(url)
                    posts.append(self._prepare(url, post.copy()))

            if self.external:  # external links
                url = post.get("permalink_url") or post.get("url")
                if url:
                    post["extension"] = None
                    posts.append((Message.Queue, url, post.copy()))
                    del post["extension"]

            post["count"] = len(posts)
            yield Message.Directory, post

            for num, (msg, url, post) in enumerate(posts, 1):
                post["num"] = num
                post["count"] = len(posts)
                yield msg, url, post

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
        post["hash"] = post["filename"].partition("_")[2]
        return Message.Url, url, post

    @staticmethod
    def _prepare_image(url, post):
        text.nameext_from_url(url, post)

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
        post["num"] = post["count"] = 1
        post["blog"] = blog
        post["reblogged"] = False
        post["type"] = post["id"] = post["hash"] = "avatar"
        return Message.Url, url, post

    def _skip_reblog(self, _):
        return not self.reblogs

    def _skip_reblog_same_blog(self, post):
        return self.blog != post.get("reblogged_root_uuid")

    def _original_photo(self, url):
        resized = url.replace("/s2048x3072/", "/s99999x99999/", 1)
        return self._update_image_token(resized)

    def _original_inline_image(self, url):
        if self.original:
            resized, n = self._subn_orig_image("/s99999x99999/", url, 1)
            if n:
                return self._update_image_token(resized)
        return self._sub_image(r"https://\1_1280.\2", url), False

    def _original_video(self, url):
        return self._sub_video(r"https://\1.\2", url)

    def _update_image_token(self, resized):
        headers = {"Accept": "text/html,*/*;q=0.8"}
        try:
            response = self.request(resized, headers=headers)
        except Exception:
            return resized, True
        else:
            updated = text.extract(response.text, '" src="', '"')[0]
            return updated, (resized == updated)

    def _original_image_fallback(self, url, post_id):
        for _ in range(3):
            self.sleep(120, "image token")
            yield self._update_image_token(url)[0]
        self.log.warning("Unable to fetch higher-resolution "
                         "version of %s (%s)", url, post_id)


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
        ("https://www.tumblr.com/blog/view/smarties-art"),
        ("https://www.tumblr.com/blog/smarties-art"),
        ("https://www.tumblr.com/smarties-art"),
    )

    def posts(self):
        return self.api.posts(self.blog, {})


class TumblrPostExtractor(TumblrExtractor):
    """Extractor for images from a single post on tumblr"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"/(?:post/|image/)?(\d+)"
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
        ("https://kichatundk.tumblr.com/post/654953419288821760", {
            "count": 2,  # high-quality images (#1846)
            "content": "d6fcc7b6f750d835d55c7f31fa3b63be26c9f89b",
        }),
        ("https://hameru-is-cool.tumblr.com/post/639261855227002880", {
            "count": 2,  # high-quality images (#1344)
            "content": "6bc19a42787e46e1bba2ef4aeef5ca28fcd3cd34",
        }),
        ("https://mikf123.tumblr.com/image/689860196535762944", {
            "pattern": r"^https://\d+\.media\.tumblr\.com"
                       r"/134791621559a79793563b636b5fe2c6"
                       r"/8f1131551cef6e74-bc/s99999x99999"
                       r"/188cf9b8915b0d0911c6c743d152fc62e8f38491\.png$",
        }),
        ("http://ziemniax.tumblr.com/post/109697912859/", {
            "exception": exception.NotFoundError,  # HTML response (#297)
        }),
        ("http://demo.tumblr.com/image/459265350"),
        ("https://www.tumblr.com/blog/view/smarties-art/686047436641353728"),
        ("https://www.tumblr.com/blog/smarties-art/686047436641353728"),
        ("https://www.tumblr.com/smarties-art/686047436641353728"),
    )

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.post_id = match.group(4)
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
    test = (
        ("http://demo.tumblr.com/tagged/Times%20Square", {
            "pattern": r"https://\d+\.media\.tumblr\.com"
                       r"/tumblr_[^/_]+_1280.jpg",
            "count": 1,
        }),
        ("https://www.tumblr.com/blog/view/smarties-art/tagged/undertale"),
        ("https://www.tumblr.com/blog/smarties-art/tagged/undertale"),
        ("https://www.tumblr.com/smarties-art/tagged/undertale"),
    )

    def __init__(self, match):
        TumblrExtractor.__init__(self, match)
        self.tag = text.unquote(match.group(4).replace("-", " "))

    def posts(self):
        return self.api.posts(self.blog, {"tag": self.tag})


class TumblrLikesExtractor(TumblrExtractor):
    """Extractor for images from a tumblr-user's liked posts"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{blog_name}", "likes")
    archive_fmt = "f_{blog[name]}_{id}_{num}"
    pattern = BASE_PATTERN + r"/likes"
    test = (
        ("http://mikf123.tumblr.com/likes", {
            "count": 1,
        }),
        ("https://www.tumblr.com/blog/view/mikf123/likes"),
        ("https://www.tumblr.com/blog/mikf123/likes"),
        ("https://www.tumblr.com/mikf123/likes"),
    )

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
        params["offset"] = self.extractor.config("offset") or 0
        params["limit"] = 50
        params["reblog_info"] = "true"

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
                self.log.info("Daily API rate limit exceeded")
                reset = response.headers.get("x-ratelimit-perday-reset")

                api_key = self.api_key or self.session.auth.consumer_key
                if api_key == self.API_KEY:
                    self.log.info("Register your own OAuth application and "
                                  "use its credentials to prevent this error: "
                                  "https://github.com/mikf/gallery-dl/blob/mas"
                                  "ter/docs/configuration.rst#extractortumblra"
                                  "pi-key--api-secret")

                if self.extractor.config("ratelimit") == "wait":
                    self.extractor.wait(seconds=reset)
                    return self._call(blog, endpoint, params)

                t = (datetime.now() + timedelta(seconds=float(reset))).time()
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
