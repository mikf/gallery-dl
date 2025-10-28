# -*- coding: utf-8 -*-

# Copyright 2016-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.tumblr.com/"""

from .common import Extractor, Message
from .. import text, util, dt


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

        self.api = self.utils().TumblrAPI(self)
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
                        yield Message.Directory, {"blog": blog}
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
            yield Message.Directory, post

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
