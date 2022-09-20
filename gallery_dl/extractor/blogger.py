# -*- coding: utf-8 -*-

# Copyright 2019-2022 Mike Fährmann
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
    r"(?:https?://)?([\w-]+\.blogspot\.com))")


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

        blog = self.api.blog_by_url("http://" + self.blog)
        blog["pages"] = blog["pages"]["totalItems"]
        blog["posts"] = blog["posts"]["totalItems"]
        blog["date"] = text.parse_datetime(blog["published"])
        del blog["selfLink"]

        sub = re.compile(r"(/|=)(?:s\d+|w\d+-h\d+)(?=/|$)").sub
        findall_image = re.compile(
            r'src="(https?://(?:'
            r'blogger\.googleusercontent\.com/img|'
            r'\d+\.bp\.blogspot\.com)/[^"]+)').findall
        findall_video = re.compile(
            r'src="(https?://www\.blogger\.com/video\.g\?token=[^"]+)').findall
        metadata = self.metadata()

        for post in self.posts(blog):
            content = post["content"]

            files = findall_image(content)
            for idx, url in enumerate(files):
                files[idx] = sub(r"\1s0", url).replace("http:", "https:", 1)

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

            post["author"] = post["author"]["displayName"]
            post["replies"] = post["replies"]["totalItems"]
            post["content"] = text.remove_html(content)
            post["date"] = text.parse_datetime(post["published"])
            del post["selfLink"]
            del post["blog"]

            data = {"blog": blog, "post": post}
            if metadata:
                data.update(metadata)
            yield Message.Directory, data

            for data["num"], url in enumerate(files, 1):
                data["url"] = url
                yield Message.Url, url, text.nameext_from_url(url, data)

    def posts(self, blog):
        """Return an iterable with all relevant post objects"""

    def metadata(self):
        """Return additional metadata"""


class BloggerPostExtractor(BloggerExtractor):
    """Extractor for a single blog post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"(/\d{4}/\d\d/[^/?#]+\.html)"
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
        # image URLs with width/height (#1061)
        #  ("https://aaaninja.blogspot.com/2020/08/altera-boob-press-2.html", {
        #      "pattern": r"https://1.bp.blogspot.com/.+/s0/altera_.+png",
        #  }),
        # new image domain (#2204)
        (("https://randomthingsthroughmyletterbox.blogspot.com/2022/01"
          "/bitter-flowers-by-gunnar-staalesen-blog.html"), {
            "pattern": r"https://blogger.googleusercontent.com/img/a/.+=s0$",
            "count": 8,
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
    """Extractor for Blogger search resuls"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?q=([^&#]+)"
    test = (
        ("https://julianbphotography.blogspot.com/search?q=400mm", {
            "count": "< 10",
            "keyword": {"query": "400mm"},
        }),
    )

    def __init__(self, match):
        BloggerExtractor.__init__(self, match)
        self.query = text.unquote(match.group(3))

    def posts(self, blog):
        return self.api.blog_search(blog["id"], self.query)

    def metadata(self):
        return {"query": self.query}


class BloggerLabelExtractor(BloggerExtractor):
    """Extractor for Blogger posts by label"""
    subcategory = "label"
    pattern = BASE_PATTERN + r"/search/label/([^/?#]+)"
    test = (
        ("https://dmmagazine.blogspot.com/search/label/D%26D", {
            "range": "1-25",
            "count": 25,
            "keyword": {"label": "D&D"},
        }),
    )

    def __init__(self, match):
        BloggerExtractor.__init__(self, match)
        self.label = text.unquote(match.group(3))

    def posts(self, blog):
        return self.api.blog_posts(blog["id"], self.label)

    def metadata(self):
        return {"label": self.label}


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
