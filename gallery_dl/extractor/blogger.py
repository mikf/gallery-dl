# -*- coding: utf-8 -*-

# Copyright 2019-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for Blogger blogs"""

from .common import BaseExtractor, Message
from .. import text, util


def original(url):
    return (util.re(r"(/|=)(?:[sw]\d+|w\d+-h\d+)(?=/|$)")
            .sub(r"\1s0", url)
            .replace("http:", "https:", 1))


class BloggerExtractor(BaseExtractor):
    """Base class for blogger extractors"""
    basecategory = "blogger"
    directory_fmt = ("blogger", "{blog[name]}",
                     "{post[date]:%Y-%m-%d} {post[title]}")
    filename_fmt = "{num:>03}.{extension}"
    archive_fmt = "{post[id]}_{num}"

    def _init(self):
        self.api = BloggerAPI(self)
        self.blog = self.root.rpartition("/")[2]
        self.videos = self.config("videos", True)

    def items(self):
        blog = self.api.blog_by_url("http://" + self.blog)
        blog["pages"] = blog["pages"]["totalItems"]
        blog["posts"] = blog["posts"]["totalItems"]
        blog["date"] = text.parse_datetime(blog["published"])
        del blog["selfLink"]

        findall_image = util.re(
            r'src="(https?://(?:'
            r'blogger\.googleusercontent\.com/img|'
            r'lh\d+(?:-\w+)?\.googleusercontent\.com|'
            r'\d+\.bp\.blogspot\.com)/[^"]+)').findall
        findall_video = util.re(
            r'src="(https?://www\.blogger\.com/video\.g\?token=[^"]+)').findall
        metadata = self.metadata()

        for post in self.posts(blog):
            content = post["content"]

            files = findall_image(content)
            for idx, url in enumerate(files):
                files[idx] = original(url)

            if self.videos and 'id="BLOG_video-' in content:
                page = self.request(post["url"]).text
                for url in findall_video(page):
                    page = self.request(url).text
                    video_config = util.json_loads(text.extr(
                        page, 'var VIDEO_CONFIG =', '\n'))
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


BASE_PATTERN = BloggerExtractor.update({
    "blogspot": {
        "root": None,
        "pattern": r"[\w-]+\.blogspot\.com",
    },
})


class BloggerPostExtractor(BloggerExtractor):
    """Extractor for a single blog post"""
    subcategory = "post"
    pattern = BASE_PATTERN + r"(/\d\d\d\d/\d\d/[^/?#]+\.html)"
    example = "https://BLOG.blogspot.com/1970/01/TITLE.html"

    def posts(self, blog):
        return (self.api.post_by_path(blog["id"], self.groups[-1]),)


class BloggerBlogExtractor(BloggerExtractor):
    """Extractor for an entire Blogger blog"""
    subcategory = "blog"
    pattern = BASE_PATTERN + r"/?$"
    example = "https://BLOG.blogspot.com/"

    def posts(self, blog):
        return self.api.blog_posts(blog["id"])


class BloggerSearchExtractor(BloggerExtractor):
    """Extractor for Blogger search resuls"""
    subcategory = "search"
    pattern = BASE_PATTERN + r"/search/?\?q=([^&#]+)"
    example = "https://BLOG.blogspot.com/search?q=QUERY"

    def metadata(self):
        self.query = query = text.unquote(self.groups[-1])
        return {"query": query}

    def posts(self, blog):
        return self.api.blog_search(blog["id"], self.query)


class BloggerLabelExtractor(BloggerExtractor):
    """Extractor for Blogger posts by label"""
    subcategory = "label"
    pattern = BASE_PATTERN + r"/search/label/([^/?#]+)"
    example = "https://BLOG.blogspot.com/search/label/LABEL"

    def metadata(self):
        self.label = label = text.unquote(self.groups[-1])
        return {"label": label}

    def posts(self, blog):
        return self.api.blog_posts(blog["id"], self.label)


class BloggerAPI():
    """Minimal interface for the Blogger API v3

    https://developers.google.com/blogger
    """
    API_KEY = "AIzaSyCN9ax34oMMyM07g_M-5pjeDp_312eITK8"

    def __init__(self, extractor):
        self.extractor = extractor
        self.api_key = extractor.config("api-key") or self.API_KEY

    def blog_by_url(self, url):
        return self._call("/blogs/byurl", {"url": url}, "blog")

    def blog_posts(self, blog_id, label=None):
        endpoint = f"/blogs/{blog_id}/posts"
        params = {"labels": label}
        return self._pagination(endpoint, params)

    def blog_search(self, blog_id, query):
        endpoint = f"/blogs/{blog_id}/posts/search"
        params = {"q": query}
        return self._pagination(endpoint, params)

    def post_by_path(self, blog_id, path):
        endpoint = f"/blogs/{blog_id}/posts/bypath"
        return self._call(endpoint, {"path": path}, "post")

    def _call(self, endpoint, params, notfound=None):
        url = "https://www.googleapis.com/blogger/v3" + endpoint
        params["key"] = self.api_key
        return self.extractor.request_json(
            url, params=params, notfound=notfound)

    def _pagination(self, endpoint, params):
        while True:
            data = self._call(endpoint, params)
            if "items" in data:
                yield from data["items"]
            if "nextPageToken" not in data:
                return
            params["pageToken"] = data["nextPageToken"]
