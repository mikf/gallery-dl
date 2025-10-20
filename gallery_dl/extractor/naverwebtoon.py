# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
# Copyright 2022-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import text

BASE_PATTERN = (r"(?:https?://)?comic\.naver\.com"
                r"/(webtoon|challenge|bestChallenge)")


class NaverWebtoonBase():
    """Base class for comic.naver.com extractors"""
    category = "naver-webtoon"
    root = "https://comic.naver.com"


class NaverWebtoonEpisodeExtractor(NaverWebtoonBase, GalleryExtractor):
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode:>03}-{num:>02}.{extension}"
    archive_fmt = "{title_id}_{episode}_{num}"
    pattern = rf"{BASE_PATTERN}/detail(?:\.nhn)?\?([^#]+)"
    example = "https://comic.naver.com/webtoon/detail?titleId=12345&no=1"

    def __init__(self, match):
        path, query = match.groups()
        url = f"{self.root}/{path}/detail?{query}"
        GalleryExtractor.__init__(self, match, url)

        query = text.parse_query(query)
        self.title_id = query.get("titleId")
        self.episode = query.get("no")

    def metadata(self, page):
        extr = text.extract_from(page)
        return {
            "title_id": self.title_id,
            "episode" : self.episode,
            "comic"   : extr('titleName: "', '"'),
            "tags"    : [t.strip() for t in text.extract_iter(
                extr("tagList: [", "],"), '"tagName":"', '"')],
            "title"   : extr('"subtitle":"', '"'),
            "author"  : [a.strip() for a in text.extract_iter(
                extr('"writers":[', ']'), '"name":"', '"')],
            "artist"  : [a.strip() for a in text.extract_iter(
                extr('"painters":[', ']'), '"name":"', '"')]
        }

    def images(self, page):
        view_area = text.extr(page, 'id="comic_view_area"', '</div>')
        return [
            (url, None)
            for url in text.extract_iter(view_area, '<img src="', '"')
            if "/static/" not in url
        ]


class NaverWebtoonComicExtractor(NaverWebtoonBase, Extractor):
    subcategory = "comic"
    categorytransfer = True
    pattern = rf"{BASE_PATTERN}/list(?:\.nhn)?\?([^#]+)"
    example = "https://comic.naver.com/webtoon/list?titleId=12345"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, query = match.groups()
        query = text.parse_query(query)
        self.title_id = query.get("titleId")
        self.page_no = text.parse_int(query.get("page"), 1)
        self.sort = query.get("sort", "ASC")

    def items(self):
        url = self.root + "/api/article/list"
        headers = {
            "Accept": "application/json, text/plain, */*",
        }
        params = {
            "titleId": self.title_id,
            "page"   : self.page_no,
            "sort"   : self.sort,
        }

        while True:
            data = self.request_json(url, headers=headers, params=params)

            path = data["webtoonLevelCode"].lower().replace("_c", "C", 1)
            base = f"{self.root}/{path}/detail?titleId={data['titleId']}&no="

            for article in data["articleList"]:
                article["_extractor"] = NaverWebtoonEpisodeExtractor
                yield Message.Queue, base + str(article["no"]), article

            params["page"] = data["pageInfo"]["nextPage"]
            if not params["page"]:
                return
