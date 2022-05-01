# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
# Copyright 2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text
import re

BASE_PATTERN = (r"(?:https?://)?comic\.naver\.com"
                r"/(webtoon|challenge|bestChallenge)")


class NaverwebtoonBase():
    """Base class for naver webtoon extractors"""
    category = "naverwebtoon"
    root = "https://comic.naver.com"


class NaverwebtoonEpisodeExtractor(NaverwebtoonBase, GalleryExtractor):
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode:>03}-{num:>02}.{extension}"
    archive_fmt = "{title_id}_{episode}_{num}"
    pattern = BASE_PATTERN + r"/detail(?:\.nhn)?\?([^#]+)"
    test = (
        (("https://comic.naver.com/webtoon/detail"
          "?titleId=26458&no=1&weekday=tue"), {
            "url": "47a956ba8c7a837213d5985f50c569fcff986f75",
            "content": "3806b6e8befbb1920048de9888dfce6220f69a60",
            "count": 14
        }),
        (("https://comic.naver.com/challenge/detail"
          "?titleId=765124&no=1"), {
            "pattern": r"https://image-comic\.pstatic\.net/nas"
                       r"/user_contents_data/challenge_comic/2021/01/19"
                       r"/342586/upload_7149856273586337846\.jpeg",
            "count": 1,
        }),
        (("https://comic.naver.com/bestChallenge/detail.nhn"
          "?titleId=771467&no=3"), {
            "pattern": r"https://image-comic\.pstatic\.net/nas"
                       r"/user_contents_data/challenge_comic/2021/04/28"
                       r"/345534/upload_3617293622396203109\.jpeg",
            "count": 1,
        }),
    )

    def __init__(self, match):
        path, query = match.groups()
        url = "{}/{}/detail?{}".format(self.root, path, query)
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
    pattern = (BASE_PATTERN + r"/list(?:\.nhn)?\?([^#]+)")
    test = (
        ("https://comic.naver.com/webtoon/list?titleId=22073", {
            "pattern": NaverwebtoonEpisodeExtractor.pattern,
            "count": 32,
        }),
        ("https://comic.naver.com/challenge/list?titleId=765124", {
            "pattern": NaverwebtoonEpisodeExtractor.pattern,
            "count": 25,
        }),
        ("https://comic.naver.com/bestChallenge/list.nhn?titleId=789786", {
            "pattern": NaverwebtoonEpisodeExtractor.pattern,
            "count": ">= 12",
        }),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, query = match.groups()
        query = text.parse_query(query)
        self.title_id = query.get("titleId")
        self.page_no = text.parse_int(query.get("page"), 1)

    def items(self):
        url = "{}/{}/list".format(self.root, self.path)
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
            self.root + path
            for path in re.findall(
                r'<a href="(/(?:webtoon|challenge|bestChallenge)'
                r'/detail\?[^"]+)', page)
        ][::2]
