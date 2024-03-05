# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
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
               r"(?:PostView\.n(?:aver|hn)\?blogId=(\w+)&logNo=(\d+)|"
               r"(\w+)/(\d+)/?$)")
    example = "https://blog.naver.com/BLOGID/12345"

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
                "title"      : text.unescape(extr(
                    '"og:title" content="', '"')),
                "description": text.unescape(extr(
                    '"og:description" content="', '"')).replace("&nbsp;", " "),
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
        results = []
        for url in text.extract_iter(page, 'data-lazy-src="', '"'):
            url = url.replace("://post", "://blog", 1).partition("?")[0]
            if "\ufffd" in text.unquote(url):
                url = text.unquote(url, encoding="EUC-KR")
            results.append((url, None))
        return results


class NaverBlogExtractor(NaverBase, Extractor):
    """Extractor for a user's blog on blog.naver.com"""
    subcategory = "blog"
    categorytransfer = True
    pattern = (r"(?:https?://)?blog\.naver\.com/"
               r"(?:PostList\.n(?:aver|hn)\?(?:[^&#]+&)*blogId=([^&#]+)|"
               r"(\w+)/?$)")
    example = "https://blog.naver.com/BLOGID"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.blog_id = match.group(1) or match.group(2)

    def items(self):
        # fetch first post number
        url = "{}/PostList.nhn?blogId={}".format(self.root, self.blog_id)
        post_num = text.extr(
            self.request(url).text, 'gnFirstLogNo = "', '"',
        )

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
