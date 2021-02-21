# -*- coding: utf-8 -*-

# Copyright 2021 Seonghyeon Cho
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://comic.naver.com/"""

from .common import Extractor, Message
from .. import exception, text

BASE_PATTERN = r"(?:(?:https?://)?comic\.naver\.com)?/("


class NaverwebtoonExtractor(Extractor):
    category = "naverwebtoon"
    root = "https://comic.naver.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.path, self.query = match.gropus()

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)
        return response


class NaverwebtoonEpisodeExtractor(NaverwebtoonExtractor):
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode}-{num:>02}.{extension}"
    archive_fmt = "{title_id}_{episode}_{num}"
    pattern = (BASE_PATTERN + r"/webtoon)/detail.nhn\?([^/&#]+)")
    test = (
        (("https://comic.naver.com/webtoon/detail.nhn?"
          "titleId=26458&no=1&weekday=tue"), {
            "url": "",
            "content": "",
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
        url = "{}/{}/detail.nhn?{}".format(self.root, self.path, self.query)
        page = self.request(url).text
        data = self.get_job_metadata(page)

        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(self.get_image_urls(page), 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title, pos = text.extract(page, '<meta property="og:title" content="', '"')
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
        return list(text.extract_iter(page, '<div class="wt_viewer" style="background:#FFFFFF">', '</div>'))


class NaverwebtoonComicExtractor(NaverwebtoonExtractor):
    subcategory = "comic"
    categorytransfer = True
    pattern = (BASE_PATTERN + r"/webtoon)/list.nhn\?([^/&#]+)")
    test = (
        ("https://comic.naver.com/webtoon/list.nhn?titleId=26458", {
            "pattern": NaverwebtoonEpisodeExtractor.pattern,
            # "range": "",
            "count": ">= 10",
        }),
    )

    def __init__(self, match):
        NaverwebtoonExtractor.__init__(self, match)
        query = text.parse_query(self.query)
        self.title_id = query.get("titleId")
        if not self.title_id:
            raise exception.NotFoundError("titleId")
        self.page_no = int(query.get("page", 1))

    def items(self):
        page = None
        data = {"_extractor": NaverwebtoonEpisodeExtractor}

        while True:
            path = "/{}/list.nhn?titleId={}&page={}".format(
                self.path, self.title_id, self.page_no)

            if page and path not in page:
                return

            page = self.request(self.root + path).text
            data["page"] = self.page_no

            for url in self.get_episode_urls(page):
                yield Message.Queue, url, data

            self.page_no += 1

    @staticmethod
    def get_episode_urls(page):
        """Extract and return all episode urls in page"""
        page = text.extract(page, 'class="viewList"', '</table>')[0]
        return [
            match.group(0)
            for match in NaverwebtoonEpisodeExtractor.pattern.finditer(page)
        ]
