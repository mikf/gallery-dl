# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import Extractor, Message
from .. import exception, text

BASE_PATTERN = r"(?:https?://)?comic\.naver\.com/webtoon"


class NaverwebtoonExtractor(Extractor):
    category = "naverwebtoon"
    root = "https://comic.naver.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.query = match.group(1)


class NaverwebtoonEpisodeExtractor(NaverwebtoonExtractor):
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode:>03}-{num:>02}.{extension}"
    archive_fmt = "{title_id}_{episode}_{num}"
    pattern = (BASE_PATTERN + r"/detail\.nhn\?([^#]+)")
    test = (
        (("https://comic.naver.com/webtoon/detail.nhn?"
          "titleId=26458&no=1&weekday=tue"), {
            "url": "47a956ba8c7a837213d5985f50c569fcff986f75",
            "content": "3806b6e8befbb1920048de9888dfce6220f69a60",
            "count": 14
        }),
    )

    def __init__(self, match):
        NaverwebtoonExtractor.__init__(self, match)
        query = text.parse_query(self.query)
        self.title_id = query.get("titleId")
        if not self.title_id:
            raise exception.NotFoundError("titleId")
        self.episode = query.get("no")
        if not self.episode:
            raise exception.NotFoundError("no")

    def items(self):
        url = "{}/webtoon/detail.nhn?{}".format(self.root, self.query)
        page = self.request(url).text
        data = self.get_job_metadata(page)

        yield Message.Directory, data
        for data["num"], url in enumerate(self.get_image_urls(page), 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title, pos = text.extract(page, 'property="og:title" content="', '"')
        comic, pos = text.extract(page, '<h2>', '<span', pos)
        authors, pos = text.extract(page, 'class="wrt_nm">', '</span>', pos)
        authors = authors.strip().split("/")
        descr, pos = text.extract(page, '<p class="txt">', '</p>', pos)
        genre, pos = text.extract(page, '<span class="genre">', '</span>', pos)
        date, pos = text.extract(page, '<dd class="date">', '</dd>', pos)

        return {
            "title": title,
            "comic": comic,
            "authors": authors,
            "description": descr,
            "genre": genre,
            "title_id": self.title_id,
            "episode": self.episode,
            "date": date,
        }

    @staticmethod
    def get_image_urls(page):
        view_area = text.extract(page, 'id="comic_view_area"', '</div>')[0]
        return text.extract_iter(view_area, '<img src="', '"')


class NaverwebtoonComicExtractor(NaverwebtoonExtractor):
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
        NaverwebtoonExtractor.__init__(self, match)
        query = text.parse_query(self.query)
        self.title_id = query.get("titleId")
        if not self.title_id:
            raise exception.NotFoundError("titleId")
        self.page_no = text.parse_int(query.get("page", 1))

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
                page, '<a href="/webtoon/detail.nhn?', '"')
        ][::2]
