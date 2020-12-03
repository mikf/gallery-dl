# -*- coding: utf-8 -*-

# Copyright 2019 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://blog.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text


class NaverBase():
    """Base class for naver extractors"""
    category = "naver"
    root = "https://blog.naver.com"


class NaverPostExtractor(NaverBase, GalleryExtractor):
    """Extractor for blog posts on blog.naver.com"""
    subcategory = "post"
    filename_fmt = "{num:>03}.{extension}"
    directory_fmt = ("{category}", "{blog[user]} {blog[id]}",
                     "{post[date]:%Y-%m-%d} {post[title]}")
    archive_fmt = "{blog[id]}_{post[num]}_{num}"
    pattern = (r"(?:https?://)?blog\.naver\.com/"
               r"(?:PostView\.nhn\?blogId=(\w+)&logNo=(\d+)|(\w+)/(\d+)/?$)")
    test = (
        ("https://blog.naver.com/rlfqjxm0/221430673006", {
            "url": "6c694f3aced075ed5e9511f1e796d14cb26619cc",
            "keyword": "a6e23d19afbee86b37d6e7ad934650c379d2cb1e",
        }),
        (("https://blog.naver.com/PostView.nhn"
          "?blogId=rlfqjxm0&logNo=221430673006"), {
            "url": "6c694f3aced075ed5e9511f1e796d14cb26619cc",
            "keyword": "a6e23d19afbee86b37d6e7ad934650c379d2cb1e",
        }),
    )

    def __init__(self, match):
        blog_id = match.group(1)
        if blog_id:
            self.blog_id = blog_id
            self.post_id = match.group(2)
        else:
            self.blog_id = match.group(3)
            self.post_id = match.group(4)

        url = "{}/PostView.nhn?blogId={}&logNo={}".format(
            self.root, self.blog_id, self.post_id)
        GalleryExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        data = {
            "post": {
                "title"      : extr('"og:title" content="', '"'),
                "description": extr('"og:description" content="', '"'),
                "num"        : text.parse_int(self.post_id),
            },
            "blog": {
                "id"         : self.blog_id,
                "num"        : text.parse_int(extr("var blogNo = '", "'")),
                "user"       : extr("var nickName = '", "'"),
            },
        }
        data["post"]["date"] = text.parse_datetime(
            extr('se_publishDate pcol2">', '<') or
            extr('_postAddDate">', '<'), "%Y. %m. %d. %H:%M")
        return data

    def images(self, page):
        return [
            (url.replace("://post", "://blog", 1).partition("?")[0], None)
            for url in text.extract_iter(page, 'data-lazy-src="', '"')
        ]


class NaverBlogExtractor(NaverBase, Extractor):
    """Extractor for a user's blog on blog.naver.com"""
    subcategory = "blog"
    categorytransfer = True
    pattern = (r"(?:https?://)?blog\.naver\.com/"
               r"(?:PostList.nhn\?(?:[^&#]+&)*blogId=([^&#]+)|(\w+)/?$)")
    test = (
        ("https://blog.naver.com/gukjung", {
            "pattern": NaverPostExtractor.pattern,
            "count": 12,
            "range": "1-12",
        }),
        ("https://blog.naver.com/PostList.nhn?blogId=gukjung", {
            "pattern": NaverPostExtractor.pattern,
            "count": 12,
            "range": "1-12",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.blog_id = match.group(1) or match.group(2)

    def items(self):
        yield Message.Version, 1

        # fetch first post number
        url = "{}/PostList.nhn?blogId={}".format(self.root, self.blog_id)
        post_num = text.extract(
            self.request(url).text, 'gnFirstLogNo = "', '"',
        )[0]

        # setup params for API calls
        url = "{}/PostViewBottomTitleListAsync.nhn".format(self.root)
        params = {
            "blogId"             : self.blog_id,
            "logNo"              : post_num or "0",
            "viewDate"           : "",
            "categoryNo"         : "",
            "parentCategoryNo"   : "",
            "showNextPage"       : "true",
            "showPreviousPage"   : "false",
            "sortDateInMilli"    : "",
            "isThumbnailViewType": "false",
            "countPerPage"       : "",
        }

        # loop over all posts
        while True:
            data = self.request(url, params=params).json()

            for post in data["postList"]:
                post["url"] = "{}/PostView.nhn?blogId={}&logNo={}".format(
                    self.root, self.blog_id, post["logNo"])
                post["_extractor"] = NaverPostExtractor
                yield Message.Queue, post["url"], post

            if not data["hasNextPage"]:
                return
            params["logNo"] = data["nextIndexLogNo"]
            params["sortDateInMilli"] = data["nextIndexSortDate"]
