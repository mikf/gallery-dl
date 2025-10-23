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
    return (text.re(r"(/|=)(?:[sw]\d+|w\d+-h\d+)(?=/|$)")
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
        self.api = self.utils().BloggerAPI(self)
        self.blog = self.root.rpartition("/")[2]
        self.videos = self.config("videos", True)

        if self.videos:
            self.findall_video = text.re(
                r"""src=["'](https?://www\.blogger\.com"""
                r"""/video\.g\?token=[^"']+)""").findall

    def items(self):
        blog = self.api.blog_by_url("http://" + self.blog)
        blog["pages"] = blog["pages"]["totalItems"]
        blog["posts"] = blog["posts"]["totalItems"]
        blog["date"] = self.parse_datetime_iso(blog["published"])
        del blog["selfLink"]

        findall_image = text.re(
            r'src="(https?://(?:'
            r'blogger\.googleusercontent\.com/img|'
            r'lh\d+(?:-\w+)?\.googleusercontent\.com|'
            r'\d+\.bp\.blogspot\.com)/[^"]+)').findall

        for post in self.posts(blog):
            content = post["content"]

            files = findall_image(content)
            for idx, url in enumerate(files):
                files[idx] = original(url)

            if self.videos and (
                    'id="BLOG_video-' in content or
                    'class="BLOG_video_' in content):
                self._extract_videos(files, post)

            post["author"] = post["author"]["displayName"]
            post["replies"] = post["replies"]["totalItems"]
            post["content"] = text.remove_html(content)
            post["count"] = len(files)
            post["date"] = self.parse_datetime_iso(post["published"])
            del post["selfLink"]
            del post["blog"]

            data = {"blog": blog, "post": post}
            yield Message.Directory, data
            for data["num"], url in enumerate(files, 1):
                data["url"] = url
                yield Message.Url, url, text.nameext_from_url(url, data)

    def _extract_videos(self, files, post):
        html = self.api.feeds_posts_default(
            self.blog, post)["entry"]["content"]["$t"]

        for url in self.findall_video(html):
            page = self.request(url).text
            video_config = util.json_loads(text.extr(
                page, 'var VIDEO_CONFIG =', '\n'))
            files.append(max(
                video_config["streams"],
                key=lambda x: x["format_id"],
            )["play_url"])


BASE_PATTERN = BloggerExtractor.update({
    "blogspot": {
        "root": None,
        "pattern": r"[\w-]+\.blogspot\.com",
    },
})


class BloggerPostExtractor(BloggerExtractor):
    """Extractor for a single blog post"""
    subcategory = "post"
    pattern = rf"{BASE_PATTERN}(/\d\d\d\d/\d\d/[^/?#]+\.html)"
    example = "https://BLOG.blogspot.com/1970/01/TITLE.html"

    def posts(self, blog):
        return (self.api.post_by_path(blog["id"], self.groups[-1]),)


class BloggerBlogExtractor(BloggerExtractor):
    """Extractor for an entire Blogger blog"""
    subcategory = "blog"
    pattern = rf"{BASE_PATTERN}/?$"
    example = "https://BLOG.blogspot.com/"

    def posts(self, blog):
        return self.api.blog_posts(blog["id"])


class BloggerSearchExtractor(BloggerExtractor):
    """Extractor for Blogger search resuls"""
    subcategory = "search"
    pattern = rf"{BASE_PATTERN}/search/?\?q=([^&#]+)"
    example = "https://BLOG.blogspot.com/search?q=QUERY"

    def posts(self, blog):
        self.kwdict["query"] = query = text.unquote(self.groups[-1])
        return self.api.blog_search(blog["id"], query)


class BloggerLabelExtractor(BloggerExtractor):
    """Extractor for Blogger posts by label"""
    subcategory = "label"
    pattern = rf"{BASE_PATTERN}/search/label/([^/?#]+)"
    example = "https://BLOG.blogspot.com/search/label/LABEL"

    def posts(self, blog):
        self.kwdict["label"] = label = text.unquote(self.groups[-1])
        return self.api.blog_posts(blog["id"], label)
