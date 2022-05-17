# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
# Copyright 2021-2022 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.webtoons.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import exception, text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?webtoons\.com/(([^/?#]+)"


class WebtoonsBase():
    category = "webtoons"
    root = "https://www.webtoons.com"
    cookiedomain = ".webtoons.com"

    def setup_agegate_cookies(self):
        self._update_cookies({
            "atGDPR"     : "AD_CONSENT",
            "needCCPA"   : "false",
            "needCOPPA"  : "false",
            "needGDPR"   : "false",
            "pagGDPR"    : "true",
            "ageGatePass": "true",
        })

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)
        if response.history and "/ageGate" in response.url:
            raise exception.StopExtraction(
                "HTTP redirect to age gate check ('%s')", response.request.url)
        return response


class WebtoonsEpisodeExtractor(WebtoonsBase, GalleryExtractor):
    """Extractor for an episode on webtoons.com"""
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode_no}-{num:>02}.{extension}"
    archive_fmt = "{title_no}_{episode_no}_{num}"
    pattern = (BASE_PATTERN + r"/([^/?#]+)/([^/?#]+)/(?:[^/?#]+))"
               r"/viewer(?:\?([^#'\"]+))")
    test = (
        (("https://www.webtoons.com/en/comedy/safely-endangered"
          "/ep-572-earth/viewer?title_no=352&episode_no=572"), {
            "url": "55bec5d7c42aba19e3d0d56db25fdf0b0b13be38",
            "content": ("1748c7e82b6db910fa179f6dc7c4281b0f680fa7",
                        "42055e44659f6ffc410b3fb6557346dfbb993df3",
                        "49e1f2def04c6f7a6a3dacf245a1cd9abe77a6a9"),
            "count": 5,
        }),
        (("https://www.webtoons.com/en/challenge/punderworld"
          "/happy-earth-day-/viewer?title_no=312584&episode_no=40"), {
            "keyword": {
                "comic": "punderworld",
                "description": str,
                "episode": "36",
                "episode_no": "40",
                "genre": "challenge",
                "title": r"re:^Punderworld - .+",
                "title_no": "312584",
            },
        }),
    )

    def __init__(self, match):
        self.path, self.lang, self.genre, self.comic, query = match.groups()

        url = "{}/{}/viewer?{}".format(self.root, self.path, query)
        GalleryExtractor.__init__(self, match, url)
        self.setup_agegate_cookies()

        query = text.parse_query(query)
        self.title_no = query.get("title_no")
        self.episode_no = query.get("episode_no")

    def metadata(self, page):
        keywords, pos = text.extract(
            page, '<meta name="keywords" content="', '"')
        title, pos = text.extract(
            page, '<meta property="og:title" content="', '"', pos)
        descr, pos = text.extract(
            page, '<meta property="og:description" content="', '"', pos)

        return {
            "genre"      : self.genre,
            "comic"      : self.comic,
            "title_no"   : self.title_no,
            "episode_no" : self.episode_no,
            "title"      : text.unescape(title),
            "episode"    : keywords.split(", ")[1],
            "description": text.unescape(descr),
            "lang"       : self.lang,
            "language"   : util.code_to_language(self.lang),
        }

    @staticmethod
    def images(page):
        return [
            (url.replace("://webtoon-phinf.", "://swebtoon-phinf."), None)
            for url in text.extract_iter(
                page, 'class="_images" data-url="', '"')
        ]


class WebtoonsComicExtractor(WebtoonsBase, Extractor):
    """Extractor for an entire comic on webtoons.com"""
    subcategory = "comic"
    categorytransfer = True
    pattern = (BASE_PATTERN + r"/([^/?#]+)/([^/?#]+))"
               r"/list(?:\?([^#]+))")
    test = (
        # english
        (("https://www.webtoons.com/en/comedy/live-with-yourself/"
          "list?title_no=919"), {
            "pattern": WebtoonsEpisodeExtractor.pattern,
            "range": "1-15",
            "count": ">= 15",
        }),
        # french
        (("https://www.webtoons.com/fr/romance/subzero/"
          "list?title_no=1845&page=3"), {
            "count": ">= 15",
        }),
        # (#820)
        (("https://www.webtoons.com/en/challenge/scoob-and-shag/"
          "list?title_no=210827&page=9"), {
            "count": ">= 18",
        }),
        # (#1643)
        ("https://www.webtoons.com/es/romance/lore-olympus/"
         "list?title_no=1725"),
    )

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.setup_agegate_cookies()

        self.path, self.lang, self.genre, self.comic, query = match.groups()
        query = text.parse_query(query)
        self.title_no = query.get("title_no")
        self.page_no = text.parse_int(query.get("page"), 1)

    def items(self):
        page = None
        data = {"_extractor": WebtoonsEpisodeExtractor}

        while True:
            path = "/{}/list?title_no={}&page={}".format(
                self.path, self.title_no, self.page_no)

            if page and path not in page:
                return

            page = self.request(self.root + path).text
            data["page"] = self.page_no

            for url in self.get_episode_urls(page):
                yield Message.Queue, url, data

            self.page_no += 1

    @staticmethod
    def get_episode_urls(page):
        """Extract and return all episode urls in 'page'"""
        page = text.extract(page, 'id="_listUl"', '</ul>')[0]
        return [
            match.group(0)
            for match in WebtoonsEpisodeExtractor.pattern.finditer(page)
        ]
