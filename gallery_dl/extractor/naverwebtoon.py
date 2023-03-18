# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
# Copyright 2022-2033 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

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
            "count": 14,
            "keyword": {
                "author": ["김규삼"],
                "artist": ["김규삼"],
                "comic": "N의등대-눈의등대",
                "count": 14,
                "episode": "1",
                "extension": "jpg",
                "num": int,
                "tags": ["스릴러", "완결무료", "완결스릴러"],
                "title": "n의 등대 - 눈의 등대 1화",
                "title_id": "26458",
            },
        }),
        (("https://comic.naver.com/challenge/detail"
          "?titleId=765124&no=1"), {
            "pattern": r"https://image-comic\.pstatic\.net"
                       r"/user_contents_data/challenge_comic/2021/01/19"
                       r"/342586/upload_7149856273586337846\.jpeg",
            "count": 1,
            "keyword": {
                "author": ["kemi****"],
                "artist": [],
                "comic": "우니 모두의 이야기",
                "count": 1,
                "episode": "1",
                "extension": "jpeg",
                "filename": "upload_7149856273586337846",
                "num": 1,
                "tags": ["일상툰", "우니모두의이야기", "퇴사", "입사", "신입사원",
                         "사회초년생", "회사원", "20대"],
                "title": "퇴사하다",
                "title_id": "765124",
            },
        }),
        (("https://comic.naver.com/bestChallenge/detail.nhn"
          "?titleId=771467&no=3"), {
            "pattern": r"https://image-comic\.pstatic\.net"
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
            "comic"   : extr("titleName: '", "'"),
            "tags"    : [t.strip() for t in text.extract_iter(
                extr("tagList: [", "}],"), '"tagName":"', '"')],
            "title"   : extr('"subtitle":"', '"'),
            "author"  : [a.strip() for a in text.extract_iter(
                extr('"writers":[', ']'), '"name":"', '"')],
            "artist"  : [a.strip() for a in text.extract_iter(
                extr('"painters":[', ']'), '"name":"', '"')]
        }

    @staticmethod
    def images(page):
        view_area = text.extr(page, 'id="comic_view_area"', '</div>')
        return [
            (url, None)
            for url in text.extract_iter(view_area, '<img src="', '"')
            if "/static/" not in url
        ]


class NaverwebtoonComicExtractor(NaverwebtoonBase, Extractor):
    subcategory = "comic"
    categorytransfer = True
    pattern = BASE_PATTERN + r"/list(?:\.nhn)?\?([^#]+)"
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
        self.sort = query.get("sort", "ASC")

    def items(self):
        base = "{}/{}/detail?titleId={}&no=".format(
            self.root, self.path, self.title_id)

        url = self.root + "/api/article/list"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": self.root + "/",
        }
        params = {
            "titleId": self.title_id,
            "page"   : self.page_no,
            "sort"   : self.sort,
        }

        while True:
            data = self.request(url, headers=headers, params=params).json()

            for article in data["articleList"]:
                article["_extractor"] = NaverwebtoonEpisodeExtractor
                yield Message.Queue, base + str(article["no"]), article

            params["page"] = data["pageInfo"]["nextPage"]
            if not params["page"]:
                return
