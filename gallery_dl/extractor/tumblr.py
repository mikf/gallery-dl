# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text, util, dt, oauth, exception


BASE_PATTERN = (
    r"(?:tumblr:(?:https?://)?([^/]+)|"
    r"(?:https?://)?"
    r"(?:(?:www\.)?tumblr\.com/(?:blog/(?:view/)?)?([\w-]+)|"
    r"([\w-]+\.tumblr\.com)))"
)

POST_TYPES = frozenset(("text", "quote", "link", "answer", "video",
                        "audio", "photo", "chat", "search"))


class TumblrExtractor(Extractor):
    """Base class for tumblr extractors"""
    category = "tumblr"
    directory_fmt = ("{category}", "{blog_name}")
    filename_fmt = "{category}_{blog_name}_{id}_{num:>02}.{extension}"
    archive_fmt = "{id}_{num}"

    def _init(self):
        if name := self.groups[1]:
            self.blog = f"{name}.tumblr.com"
        else:
            self.blog = self.groups[0] or self.groups[2]

        self.api = TumblrAPI(self)
        self.types = self._setup_posttypes()
        self.avatar = self.config("avatar", False)
        self.inline = self.config("inline", True)
        self.reblogs = self.config("reblogs", True)
        self.external = self.config("external", False)
        self.original = self.config("original", True)
        self.fallback_delay = self.config("fallback-delay", 120.0)
        self.fallback_retries = self.config("fallback-retries", 2)

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
        self._sub_video = text.re(
            r"https?://((?:vt|vtt|ve)(?:\.media)?\.tumblr\.com"
            r"/tumblr_[^_]+)_\d+\.([0-9a-z]+)").sub
        if self.inline:
            self._sub_image = text.re(
                r"https?://(\d+\.media\.tumblr\.com(?:/[0-9a-f]+)?"
                r"/tumblr(?:_inline)?_[^_]+)_\d+\.([0-9a-z]+)").sub
            self._subn_orig_image = text.re(r"/s\d+x\d+/").subn
            _findall_image = text.re('<img src="([^"]+)"').findall
            _findall_video = text.re('<source src="([^"]+)"').findall

        for post in self.posts():
            if self.date_min > post["timestamp"]:
                return
            if post["type"] not in self.types:
                continue

            if "blog" in post:
                blog = post["blog"]
                self.blog = blog["name"] + ".tumblr.com"
            else:
                if not blog:
                    blog = self.api.info(self.blog)
                    blog["uuid"] = self.blog

                    if self.avatar:
                        url = self.api.avatar(self.blog)
                        yield Message.Directory, "", {"blog": blog}
                        yield self._prepare_avatar(url, post.copy(), blog)

                post["blog"] = blog

            reblog = "reblogged_from_id" in post
            if reblog and self._skip_reblog(post):
                continue
            post["reblogged"] = reblog

            if "trail" in post:
                del post["trail"]
            post["date"] = self.parse_timestamp(post["timestamp"])
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

            if url := post.get("video_url"):  # type "video"
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
                if url := post.get("permalink_url") or post.get("url"):
                    post["extension"] = None
                    posts.append((Message.Queue, url, post.copy()))
                    del post["extension"]

            post["count"] = len(posts)
            yield Message.Directory, "", post

            for num, (msg, url, post) in enumerate(posts, 1):
                post["num"] = num
                post["count"] = len(posts)
                yield msg, url, post

    def items_blogs(self):
        for blog in self.blogs():
            blog["_extractor"] = TumblrUserExtractor
            yield Message.Queue, blog["url"], blog

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

            if invalid := types - POST_TYPES:
                types = types & POST_TYPES
                self.log.warning("Invalid post types: '%s'",
                                 "', '".join(sorted(invalid)))
            return types

    def _prepare(self, url, post):
        text.nameext_from_url(url, post)
        post["hash"] = post["filename"].partition("_")[2]
        return Message.Url, url, post

    def _prepare_image(self, url, post):
        text.nameext_from_url(url, post)

        # try ".gifv" (#3095)
        # it's unknown whether all gifs in this case are actually webps
        # incorrect extensions will be corrected by 'adjust-extensions'
        if post["extension"] == "gif":
            post["_fallback"] = (url + "v",)
            post["_http_headers"] = {"Accept":  # copied from chrome 106
                                     "image/avif,image/webp,image/apng,"
                                     "image/svg+xml,image/*,*/*;q=0.8"}

        parts = post["filename"].split("_")
        try:
            post["hash"] = parts[1] if parts[1] != "inline" else parts[2]
        except IndexError:
            # filename doesn't follow the usual pattern (#129)
            post["hash"] = post["filename"]

        return Message.Url, url, post

    def _prepare_avatar(self, url, post, blog):
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
            updated = text.extr(response.text, '" src="', '"')
            return updated, (resized == updated)

    def _original_image_fallback(self, url, post_id):
        for _ in util.repeat(self.fallback_retries):
            self.sleep(self.fallback_delay, "image token")
            yield self._update_image_token(url)[0]
        self.log.warning("Unable to fetch higher-resolution "
                         "version of %s (%s)", url, post_id)


class TumblrUserExtractor(TumblrExtractor):
    """Extractor for a Tumblr user's posts"""
    subcategory = "user"
    pattern = rf"{BASE_PATTERN}(?:/page/\d+|/archive)?/?$"
    example = "https://www.tumblr.com/BLOG"

    def posts(self):
        return self.api.posts(self.blog, {})


class TumblrPostExtractor(TumblrExtractor):
    """Extractor for a single Tumblr post"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}/(?:post/|image/)?(\d+)"
    example = "https://www.tumblr.com/BLOG/12345"

    def posts(self):
        self.reblogs = True
        self.date_min = 0
        return self.api.posts(self.blog, {"id": self.groups[3]})

    def _setup_posttypes(self):
        return POST_TYPES


class TumblrTagExtractor(TumblrExtractor):
    """Extractor for Tumblr user's posts by tag"""
    subcategory = "tag"
    pattern = rf"{BASE_PATTERN}(?:/archive)?/tagged/([^/?#]+)"
    example = "https://www.tumblr.com/BLOG/tagged/TAG"

    def posts(self):
        self.kwdict["search_tags"] = tag = text.unquote(
            self.groups[3].replace("-", " "))
        return self.api.posts(self.blog, {"tag": tag})


class TumblrDayExtractor(TumblrExtractor):
    """Extractor for Tumblr user's posts by day"""
    subcategory = "day"
    pattern = rf"{BASE_PATTERN}/day/(\d\d\d\d/\d\d/\d\d)"
    example = "https://www.tumblr.com/BLOG/day/1970/01/01"

    def posts(self):
        year, month, day = self.groups[3].split("/")
        ordinal = dt.date(int(year), int(month), int(day)).toordinal()

        # 719163 == date(1970, 1, 1).toordinal()
        self.date_min = (ordinal - 719163) * 86400
        self.api.before = self.date_min + 86400
        return self.api.posts(self.blog, {})


class TumblrLikesExtractor(TumblrExtractor):
    """Extractor for a Tumblr user's liked posts"""
    subcategory = "likes"
    directory_fmt = ("{category}", "{blog_name}", "likes")
    archive_fmt = "f_{blog[name]}_{id}_{num}"
    pattern = rf"{BASE_PATTERN}/likes"
    example = "https://www.tumblr.com/BLOG/likes"

    def posts(self):
        return self.api.likes(self.blog)


class TumblrFollowingExtractor(TumblrExtractor):
    """Extractor for a Tumblr user's followed blogs"""
    subcategory = "following"
    pattern = rf"{BASE_PATTERN}/following"
    example = "https://www.tumblr.com/BLOG/following"

    items = TumblrExtractor.items_blogs

    def blogs(self):
        return self.api.following(self.blog)


class TumblrFollowersExtractor(TumblrExtractor):
    """Extractor for a Tumblr user's followers"""
    subcategory = "followers"
    pattern = rf"{BASE_PATTERN}/followers"
    example = "https://www.tumblr.com/BLOG/followers"

    items = TumblrExtractor.items_blogs

    def blogs(self):
        return self.api.followers(self.blog)


class TumblrSearchExtractor(TumblrExtractor):
    """Extractor for a Tumblr search"""
    subcategory = "search"
    pattern = (r"(?:https?://)?(?:www\.)?tumblr\.com/search/([^/?#]+)"
               r"(?:/([^/?#]+)(?:/([^/?#]+))?)?(?:/?\?([^#]+))?")
    example = "https://www.tumblr.com/search/QUERY"

    def posts(self):
        search, mode, post_type, query = self.groups
        params = text.parse_query(query)
        return self.api.search(text.unquote(search), params, mode, post_type)


class TumblrAPI(oauth.OAuth1API):
    """Interface for the Tumblr API v2

    https://github.com/tumblr/docs/blob/master/api.md
    """
    ROOT = "https://api.tumblr.com"
    API_KEY = "O3hU2tMi5e4Qs5t3vezEi6L0qRORJ5y9oUpSGsrWu8iA3UCc3B"
    API_SECRET = "sFdsK3PDdP2QpYMRAoq0oDnw0sFS24XigXmdfnaeNZpJpqAn03"
    BLOG_CACHE = {}

    def __init__(self, extractor):
        oauth.OAuth1API.__init__(self, extractor)
        self.posts_type = self.before = None

    def info(self, blog):
        """Return general information about a blog"""
        try:
            return self.BLOG_CACHE[blog]
        except KeyError:
            endpoint = f"/v2/blog/{blog}/info"
            params = {"api_key": self.api_key} if self.api_key else None
            self.BLOG_CACHE[blog] = blog = self._call(endpoint, params)["blog"]
            return blog

    def avatar(self, blog, size="512"):
        """Retrieve a blog avatar"""
        if self.api_key:
            return (f"{self.ROOT}/v2/blog/{blog}/avatar/{size}"
                    f"?api_key={self.api_key}")
        endpoint = f"/v2/blog/{blog}/avatar"
        params = {"size": size}
        return self._call(
            endpoint, params, allow_redirects=False)["avatar_url"]

    def posts(self, blog, params):
        """Retrieve published posts"""
        params["offset"] = self.extractor.config("offset")
        params["limit"] = 50
        params["reblog_info"] = "true"
        params["type"] = self.posts_type
        params["before"] = self.before

        if self.before and params["offset"]:
            self.log.warning("'offset' and 'date-max' cannot be used together")

        endpoint = f"/v2/blog/{blog}/posts"
        return self._pagination(endpoint, params, blog=blog, cache=True)

    def likes(self, blog):
        """Retrieve liked posts"""
        endpoint = f"/v2/blog/{blog}/likes"
        params = {"limit": "50", "before": self.before}
        if self.api_key:
            params["api_key"] = self.api_key

        while True:
            posts = self._call(endpoint, params)["liked_posts"]
            if not posts:
                return
            yield from posts
            params["before"] = posts[-1]["liked_timestamp"]

    def following(self, blog):
        endpoint = f"/v2/blog/{blog}/following"
        return self._pagination_blogs(endpoint)

    def followers(self, blog):
        endpoint = f"/v2/blog/{blog}/followers"
        return self._pagination_blogs(endpoint)

    def search(self, query, params, mode="top", post_type=None):
        """Retrieve search results"""
        endpoint = "/v2/timeline/search"

        params["limit"] = "50"
        params["days"] = params.pop("t", None)
        params["query"] = query
        params["mode"] = mode
        params["reblog_info"] = "true" if self.extractor.reblogs else "false"
        if post_type:
            params["post_type_filter"] = post_type

        return self._pagination(endpoint, params)

    def _call(self, endpoint, params, **kwargs):
        url = self.ROOT + endpoint
        kwargs["params"] = params

        while True:
            response = self.request(url, **kwargs)

            try:
                data = response.json()
            except ValueError:
                data = response.text
                status = response.status_code
            else:
                status = data["meta"]["status"]
                if 200 <= status < 400:
                    return data["response"]

            self.log.debug(data)

            if status == 403:
                raise exception.AuthorizationError()

            elif status == 404:
                try:
                    error = data["errors"][0]["detail"]
                    board = ("only viewable within the Tumblr dashboard"
                             in error)
                except Exception:
                    board = False

                if board:
                    if self.api_key is None:
                        self.log.info(
                            "Ensure your 'access-token' and "
                            "'access-token-secret' belong to the same "
                            "application as 'api-key' and 'api-secret'")
                    else:
                        self.log.info("Run 'gallery-dl oauth:tumblr' "
                                      "to access dashboard-only blogs")
                    raise exception.AuthorizationError(error)
                raise exception.NotFoundError("user or post")

            elif status == 429:
                # daily rate limit
                if response.headers.get("x-ratelimit-perday-remaining") == "0":
                    self.log.info("Daily API rate limit exceeded")
                    reset = response.headers.get("x-ratelimit-perday-reset")

                    api_key = self.api_key or self.session.auth.consumer_key
                    if api_key == self.API_KEY:
                        self.log.info(
                            "Register your own OAuth application and use its "
                            "credentials to prevent this error: "
                            "https://gdl-org.github.io/docs/configuration.html"
                            "#extractor-tumblr-api-key-api-secret")

                    if self.extractor.config("ratelimit") == "wait":
                        self.extractor.wait(seconds=reset)
                        continue

                    t = (dt.now() + dt.timedelta(0, float(reset))).time()
                    raise exception.AbortExtraction(
                        f"Aborting - Rate limit will reset at "
                        f"{t.hour:02}:{t.minute:02}:{t.second:02}")

                # hourly rate limit
                if reset := response.headers.get("x-ratelimit-perhour-reset"):
                    self.log.info("Hourly API rate limit exceeded")
                    self.extractor.wait(seconds=reset)
                    continue

            raise exception.AbortExtraction(data)

    def _pagination(self, endpoint, params,
                    blog=None, key="posts", cache=False):
        if self.api_key:
            params["api_key"] = self.api_key

        strategy = self.extractor.config("pagination")
        if not strategy:
            if params.get("before"):
                strategy = "before"
            elif "offset" not in params:
                strategy = "api"

        while True:
            data = self._call(endpoint, params)

            if "timeline" in data:
                data = data["timeline"]
                posts = data["elements"]

            else:
                if cache:
                    self.BLOG_CACHE[blog] = data["blog"]
                    cache = False
                posts = data[key]

            yield from posts

            if strategy == "api":
                try:
                    endpoint = data["_links"]["next"]["href"]
                except KeyError:
                    return
                if params is not None and self.api_key:
                    endpoint = f"{endpoint}&api_key={self.api_key}"
                    params = None

            elif strategy == "before":
                if not posts:
                    return
                timestamp = posts[-1]["timestamp"] + 1
                if params["before"] and timestamp >= params["before"]:
                    return
                params["before"] = timestamp
                params["offset"] = None

            else:  # offset
                params["offset"] = \
                    text.parse_int(params["offset"]) + params["limit"]
                params["before"] = None
                if params["offset"] >= data["total_posts"]:
                    return

    def _pagination_blogs(self, endpoint, params=None):
        if params is None:
            params = {}
        if self.api_key:
            params["api_key"] = self.api_key
        params["limit"] = 20
        params["offset"] = text.parse_int(params.get("offset"), 0)

        while True:
            data = self._call(endpoint, params)

            blogs = data["blogs"]
            yield from blogs

            params["offset"] = params["offset"] + params["limit"]
            if params["offset"] >= data["total_blogs"]:
                return
