# -*- coding: utf-8 -*-

# Copyright 2019-2020 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Blogger blogs"""

from .common import Extractor, Message
from .. import text
import json
import re

BASE_PATTERN = (
    r"(?:blogger:(?:https?://)?([^/]+)|"
    r"(?:https?://)?([^.]+\.blogspot\.com))")


class BloggerExtractor(Extractor):
    """Base class for blogger extractors"""
    category = "blogger"
    directory_fmt = ("{category}", "{blog[name]}",
                     "{post[date]:%Y-%m-%d} {post[title]}")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{post[id]}_{num}"
    root = "https://www.blogger.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.videos = self.config("videos", True)
        self.blog = match.group(1) or match.group(2)
        self.api = BloggerAPI(self)

    def items(self):
        yield Message.Version, 1

        blog = self.api.blog_by_url("http://" + self.blog)
        blog["pages"] = blog["pages"]["totalItems"]
        blog["posts"] = blog["posts"]["totalItems"]
        blog["date"] = text.parse_datetime(blog["published"])
        del blog["selfLink"]

        sub = re.compile(r"/s\d+/").sub
        findall_image = re.compile(
            r'src="(https?://\d+\.bp\.blogspot\.com/[^"]+)').findall
        findall_video = re.compile(
            r'src="(https?://www\.blogger\.com/video\.g\?token=[^"]+)').findall

        for post in self.posts(blog):
            content = post["content"]

            files = findall_image(content)
            for idx, url in enumerate(files):
                files[idx] = sub("/s0/", url).replace("http:", "https:", 1)

            if self.videos and 'id="BLOG_video-' in content:
                page = self.request(post["url"]).text
                for url in findall_video(page):
                    page = self.request(url).text
                    video_config = json.loads(text.extract(
                        page, 'var VIDEO_CONFIG =', '\n')[0])
                    files.append(max(
                        video_config["streams"],
                        key=lambda x: x["format_id"],
                    )["play_url"])

            if not files:
                continue

            post["author"] = post["author"]["displayName"]
            post["replies"] = post["replies"]["totalItems"]
            post["content"] = text.remove_html(content)
            post["date"] = text.parse_datetime(post["published"])
            del post["selfLink"]
            del post["blog"]

            yield Message.Directory, {"blog": blog, "post": post}
            for num, url in enumerate(files, 1):
                yield Message.Url, url, text.nameext_from_url(url, {
                    "blog": blog,
                    "post": post,
                    "url" : url,
                    "num" : num,
                })

    def posts(self, blog):
        """Return an iterable with all relevant post objects"""


class BloggerPostExtractor(BloggerExtractor):
    """Extractor for a single blog post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"(/\d{4}/\d\d/[^/?&#]+\.html)"
    test = (
        ("https://julianbphotography.blogspot.com/2010/12/moon-rise.html", {
            "url": "9928429fb62f712eb4de80f53625eccecc614aae",
            "pattern": r"https://3.bp.blogspot.com/.*/s0/Icy-Moonrise-.*.jpg",
            "keyword": {
                "blog": {
                    "date"       : "dt:2010-11-21 18:19:42",
                    "description": "",
                    "id"         : "5623928067739466034",
                    "kind"       : "blogger#blog",
                    "locale"     : dict,
                    "name"       : "Julian Bunker Photography",
                    "pages"      : int,
                    "posts"      : int,
                    "published"  : "2010-11-21T10:19:42-08:00",
                    "updated"    : str,
                    "url"        : "http://julianbphotography.blogspot.com/",
                },
                "post": {
                    "author"     : "Julian Bunker",
                    "content"    : str,
                    "date"       : "dt:2010-12-26 01:08:00",
                    "etag"       : str,
                    "id"         : "6955139236418998998",
                    "kind"       : "blogger#post",
                    "published"  : "2010-12-25T17:08:00-08:00",
                    "replies"    : "0",
                    "title"      : "Moon Rise",
                    "updated"    : "2011-12-06T05:21:24-08:00",
                    "url"        : "re:.+/2010/12/moon-rise.html$",
                },
                "num": int,
                "url": str,
            },
        }),
        ("blogger:http://www.julianbunker.com/2010/12/moon-rise.html"),
        # video (#587)
        (("http://cfnmscenesinmovies.blogspot.com/2011/11/"
          "cfnm-scene-jenna-fischer-in-office.html"), {
            "pattern": r"https://.+\.googlevideo\.com/videoplayback",
        }),
    )

    def __init__(self, match):
        BloggerExtractor.__init__(self, match)
        self.path = match.group(3)

    def posts(self, blog):
        return (self.api.post_by_path(blog["id"], self.path),)


class BloggerBlogExtractor(BloggerExtractor):
    """Extractor for an entire Blogger blog"""
    subcategory = "blog"
    pattern = BASE_PATTERN + r"/?$"
    test = (
        ("https://julianbphotography.blogspot.com/", {
            "range": "1-25",
            "count": 25,
            "pattern": r"https://\d\.bp\.blogspot\.com/.*/s0/[^.]+\.jpg",
        }),
        ("blogger:https://www.kefblog.com.ng/", {
            "range": "1-25",
            "count": 25,
        }),
    )

    def posts(self, blog):
        return self.api.blog_posts(blog["id"])


class BloggerSearchExtractor(BloggerExtractor):
    """Extractor for search resuls and labels"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search(?:/?\?q=([^/?&#]+)|/label/([^/?&#]+))"
    test = (
        ("https://julianbphotography.blogspot.com/search?q=400mm", {
            "count": "< 10"
        }),
        ("https://dmmagazine.blogspot.com/search/label/D%26D", {
            "range": "1-25",
            "count": 25,
        }),
    )

    def __init__(self, match):
        BloggerExtractor.__init__(self, match)
        query = match.group(3)
        if query:
            self.query, self.label = query, None
        else:
            self.query, self.label = None, match.group(4)

    def posts(self, blog):
        if self.query:
            return self.api.blog_search(blog["id"], text.unquote(self.query))
        return self.api.blog_posts(blog["id"], text.unquote(self.label))


class BloggerAPI():
    """Minimal interface for the Blogger v3 API

    Ref: https://developers.google.com/blogger
    """
    API_KEY = "AIzaSyCN9ax34oMMyM07g_M-5pjeDp_312eITK8"

    def __init__(self, extractor):
        self.extractor = extractor
        self.api_key = extractor.config("api-key", self.API_KEY)

    def blog_by_url(self, url):
        return self._call("blogs/byurl", {"url": url}, "blog")

    def blog_posts(self, blog_id, label=None):
        endpoint = "blogs/{}/posts".format(blog_id)
        params = {"labels": label}
        return self._pagination(endpoint, params)

    def blog_search(self, blog_id, query):
        endpoint = "blogs/{}/posts/search".format(blog_id)
        params = {"q": query}
        return self._pagination(endpoint, params)

    def post_by_path(self, blog_id, path):
        endpoint = "blogs/{}/posts/bypath".format(blog_id)
        return self._call(endpoint, {"path": path}, "post")

    def _call(self, endpoint, params, notfound=None):
        url = "https://www.googleapis.com/blogger/v3/" + endpoint
        params["key"] = self.api_key
        return self.extractor.request(
            url, params=params, notfound=notfound).json()

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            if "items" in data:
                yield from data["items"]
            if "nextPageToken" not in data:
                return
            params["pageToken"] = data["nextPageToken"]
