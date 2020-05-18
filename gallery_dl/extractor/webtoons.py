# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.webtoons.com/"""

from .common import Extractor, Message
from .. import exception, text


BASE_PATTERN = r"(?:https?://)?(?:www\.)?webtoons\.com/(?:en|fr)"


class WebtoonsExtractor(Extractor):
    category = "webtoons"
    cookiedomain = "www.webtoons.com"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.session.cookies.set("ageGatePass", "true",
                                 domain=self.cookiedomain)


class WebtoonsEpisodeExtractor(WebtoonsExtractor):
    """Extractor for an episode on webtoons.com"""
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode}-{num:>02}.{extension}"
    archive_fmt = "{episode}_{num}"
    pattern = (BASE_PATTERN + r"/([^/?&#]+)/([^/?&#]+)/(?:[^/?&#]+)"
               r"/viewer(?:\?([^#]+))")
    test = (
        (("https://www.webtoons.com/en/comedy/safely-endangered"
          "/ep-572-earth/viewer?title_no=352&episode_no=572"), {
            "url": "11041d71a3f92728305c11a228e77cf0f7aa02ef",
            "content": "4f7701a750368e377d65900e6e8f64a5f9cb9c86",
            "count": 5,
        }),
    )

    def __init__(self, match):
        WebtoonsExtractor.__init__(self, match)
        self.genre , self.comic, query = match.groups()
        query = text.parse_query(query)
        self.title_no = query.get("title_no")
        if not self.title_no:
            raise exception.NotFoundError("title_no")
        self.episode = query.get("episode_no")
        if not self.episode:
            raise exception.NotFoundError("episode_no")
        self.session.headers["Referer"] = self.url

    def items(self):
        page = self.request(self.url).text
        data = self.get_job_metadata(page)
        imgs = self.get_image_urls(page)
        data["count"] = len(imgs)
        yield Message.Version, 1
        yield Message.Directory, data
        for data["num"], url in enumerate(imgs, 1):
            yield Message.Url, url, text.nameext_from_url(url, data)

    def get_job_metadata(self, page):
        """Collect metadata for extractor-job"""
        title, pos = text.extract(
            page, '<meta property="og:title" content="', '"')
        descr, pos = text.extract(
            page, '<meta property="og:description" content="', '"', pos)

        return {
            "genre": self.genre,
            "comic": self.comic,
            "title_no": self.title_no,
            "episode": self.episode,
            "title": text.unescape(title),
            "description": text.unescape(descr),
        }

    @staticmethod
    def get_image_urls(page):
        """Extract and return a list of all image urls"""
        return list(text.extract_iter(page, 'class="_images" data-url="', '"'))


class WebtoonsComicExtractor(WebtoonsExtractor):
    """Extractor for an entire comic on webtoons.com"""
    subcategory = "comic"
    pattern = (BASE_PATTERN + r"/([^/?&#]+)/([^/?&#]+)"
               r"/list(?:\?([^#]+))")
    test = (
        (("https://www.webtoons.com/en/comedy/live-with-yourself/"
          "list?title_no=919"), {
            "range": "1-15",
            "count": ">= 15",
        }),
    )

    def __init__(self, match):
        WebtoonsExtractor.__init__(self, match)
        self.genre, self.comic, query = match.groups()
        query = text.parse_query(query)
        self.title_no = query.get("title_no")
        if not self.title_no:
            raise exception.NotFoundError("title_no")
        self.page_no = int(query.get("page", 1))

    def items(self):
        data = {}
        data["_extractor"] = WebtoonsEpisodeExtractor
        while True:
            page = self.request("https://www.webtoons.com/en/" +
                                self.genre + "/" + self.comic + "/list?" +
                                "title_no=" + self.title_no + "&"
                                "page=" + str(self.page_no)).text
            data["page"] = self.page_no

            for url in self.get_episode_urls(page):
                yield Message.Queue, url, data

            if not self.has_next_page(page):
                break

            self.page_no += 1

    def has_next_page(self, page):
        return "/en/" + self.genre + "/" + self.comic + "/list?" + \
               "title_no=" + self.title_no + \
               "&page=" + str(self.page_no + 1) in page

    @staticmethod
    def get_episode_urls(page):
        """Extract and return a list of all episode urls"""
        return list(text.extract_iter(page, '<a href="',
                    '" class="NPI=a:list', page.find('id="_listUl"')))
