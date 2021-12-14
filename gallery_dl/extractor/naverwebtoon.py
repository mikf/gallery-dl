# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?comic\.naver\.com/webtoon"


class NaverwebtoonBase():
    """Base class for naver webtoon extractors"""
    category = "naverwebtoon"
    root = "https://comic.naver.com"


class NaverwebtoonEpisodeExtractor(NaverwebtoonBase, GalleryExtractor):
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode:>03}-{num:>02}.{extension}"
    archive_fmt = "{title_id}_{episode}_{num}"
    pattern = BASE_PATTERN + r"/detail\.nhn\?([^#]+)"
    test = (
        (("https://comic.naver.com/webtoon/detail.nhn?"
          "titleId=26458&no=1&weekday=tue"), {
            "url": "47a956ba8c7a837213d5985f50c569fcff986f75",
            "content": "3806b6e8befbb1920048de9888dfce6220f69a60",
            "count": 14
        }),
    )

    def __init__(self, match):
        query = match.group(1)
        url = "{}/webtoon/detail.nhn?{}".format(self.root, query)
        GalleryExtractor.__init__(self, match, url)

        query = text.parse_query(query)
        self.title_id = query.get("titleId")
        self.episode = query.get("no")

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "title_id": self.title_id,
            "episode" : self.episode,
            "title"   : extr('property="og:title" content="', '"'),
            "comic"   : extr('<h2>', '<span'),
            "authors" : extr('class="wrt_nm">', '</span>').strip().split("/"),
            "description": extr('<p class="txt">', '</p>'),
            "genre"   : extr('<span class="genre">', '</span>'),
            "date"    : extr('<dd class="date">', '</dd>'),
        }

    @staticmethod
    def images(page):
        view_area = text.extract(page, 'id="comic_view_area"', '</div>')[0]
        return [
            (url, None)
            for url in text.extract_iter(view_area, '<img src="', '"')
            if "/static/" not in url
        ]


class NaverwebtoonComicExtractor(NaverwebtoonBase, Extractor):
    subcategory = "comic"
    categorytransfer = True
    pattern = (BASE_PATTERN + r"/list\.nhn\?([^#]+)")
    test = (
        ("https://comic.naver.com/webtoon/list.nhn?titleId=22073", {
            "pattern": NaverwebtoonEpisodeExtractor.pattern,
            "count": 32,
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        query = text.parse_query(match.group(1))
        self.title_id = query.get("titleId")
        self.page_no = text.parse_int(query.get("page"), 1)

    def items(self):
        url = self.root + "/webtoon/list.nhn"
        params = {"titleId": self.title_id, "page": self.page_no}
        data = {"_extractor": NaverwebtoonEpisodeExtractor}

        while True:
            page = self.request(url, params=params).text
            data["page"] = self.page_no

            for episode_url in self.get_episode_urls(page):
                yield Message.Queue, episode_url, data

            if 'class="next"' not in page:
                return
            params["page"] += 1

    def get_episode_urls(self, page):
        """Extract and return all episode urls in page"""
        return [
            self.root + "/webtoon/detail.nhn?" + query
            for query in text.extract_iter(
                page, '<a href="/webtoon/detail?', '"')
        ][::2]
