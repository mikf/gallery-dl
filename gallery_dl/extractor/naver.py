# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://blog.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
from datetime import date
import json
import urllib.request

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

        # fixes directory error for posts created less than 24 hours ago
        if "전" in str(data["post"]["date"]):
            data["post"]["date"] = text.parse_datetime(date.today().isoformat(), format="%Y-%m-%d")

        return data

    def images(self, page):
        # grab keys for json files
        keys = [
            key for key in text.extract_iter(page, 'inkey" : "', '"')
        ]

        videos = []

        if keys:
            # grab json ids
            json_ids = text.extr(page, "likeItVideoIdListJson = '", "'")

            # convert to list
            json_ids = json_ids.strip('[]').replace('"', '').replace(' ', '').split(',')
            
            # create list of json urls
            jsons = [f'https://apis.naver.com/rmcnmv/rmcnmv/vod/play/v2.0/{j}?key={k}' for j,k in zip(json_ids, keys)]
            for j in jsons:
                with urllib.request.urlopen(j) as url:
                    data = json.loads(url.read().decode())

                    # Parse source video urls and select highest quality source
                    sources = data['videos']['list']
                    sizes = [s['size'] for s in sources]
                    i = sizes.index(max(sizes))
                    videos.append((sources[i]['source'], None))

        images = [
            (url.replace("://post", "://blog", 1).partition("?")[0], None)
            for url in text.extract_iter(page, 'data-lazy-src="', '"')
        ]
        return images + videos


class NaverBlogExtractor(NaverBase, Extractor):
    """Extractor for a user's blog on blog.naver.com"""
    subcategory = "blog"
    categorytransfer = True
    pattern = (r"(?:https?://)?blog\.naver\.com/"
               r"(?:PostList.nhn\?(?:[^&#]+&)*blogId=([^&#]+)|(\w+)/?$)")
    example = "https://blog.naver.com/BLOGID"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.blog_id = match.group(1) or match.group(2)

    def items(self):

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
