# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
# Copyright 2021-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.webtoons.com/"""

from .common import GalleryExtractor, Extractor, Message
from .. import exception, text, util

BASE_PATTERN = r"(?:https?://)?(?:www\.)?webtoons\.com"
LANG_PATTERN = BASE_PATTERN + r"/(([^/?#]+)"


class WebtoonsBase():
    category = "webtoons"
    root = "https://www.webtoons.com"
    cookies_domain = ".webtoons.com"
    request_interval = (0.5, 1.5)

    def setup_agegate_cookies(self):
        self.cookies_update({
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
                "HTTP redirect to age gate check ('%s')", response.url)
        return response


class WebtoonsEpisodeExtractor(WebtoonsBase, GalleryExtractor):
    """Extractor for an episode on webtoons.com"""
    subcategory = "episode"
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode_no}-{num:>02}.{extension}"
    archive_fmt = "{title_no}_{episode_no}_{num}"
    pattern = (LANG_PATTERN + r"/([^/?#]+)/([^/?#]+)/[^/?#]+)"
               r"/viewer\?([^#'\"]+)")
    example = ("https://www.webtoons.com/en/GENRE/TITLE/NAME/viewer"
               "?title_no=123&episode_no=12345")

    def _init(self):
        self.setup_agegate_cookies()

        path, self.lang, self.genre, self.comic, query = self.groups
        params = text.parse_query(query)
        self.title_no = params.get("title_no")
        self.episode_no = params.get("episode_no")
        self.gallery_url = "{}/{}/viewer?{}".format(self.root, path, query)

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr('<meta property="og:title" content="', '"')
        descr = extr('<meta property="og:description" content="', '"')

        if extr('<div class="subj_info"', '\n'):
            comic_name = extr('>', '<')
            episode_name = extr('<h1 class="subj_episode" title="', '"')
        else:
            comic_name = episode_name = ""

        if extr('<span class="tx _btnOpenEpisodeList ', '"'):
            episode = extr('>#', '<')
        else:
            episode = ""

        if extr('<span class="author"', '\n'):
            username = extr('/u/', '"')
            author_name = extr('<span>', '</span>')
        else:
            username = author_name = ""

        return {
            "genre"       : self.genre,
            "comic"       : self.comic,
            "title_no"    : self.title_no,
            "episode_no"  : self.episode_no,
            "title"       : text.unescape(title),
            "episode"     : episode,
            "comic_name"  : text.unescape(comic_name),
            "episode_name": text.unescape(episode_name),
            "username"    : username,
            "author_name" : text.unescape(author_name),
            "description" : text.unescape(descr),
            "lang"        : self.lang,
            "language"    : util.code_to_language(self.lang),
        }

    def images(self, page):
        quality = self.config("quality")
        if quality is None or quality == "original":
            quality = {"jpg": False, "jpeg": False, "webp": False}
        elif not quality:
            quality = None
        elif isinstance(quality, str):
            quality = {"jpg": quality, "jpeg": quality}
        elif isinstance(quality, int):
            quality = "q" + str(quality)
            quality = {"jpg": quality, "jpeg": quality}
        elif not isinstance(quality, dict):
            quality = None

        results = []
        for url in text.extract_iter(
                page, 'class="_images" data-url="', '"'):

            if quality is not None:
                path, _, query = url.rpartition("?")
                type = quality.get(path.rpartition(".")[2].lower())
                if type is False:
                    url = path
                elif type:
                    url = "{}?type={}".format(path, type)

            url = url.replace("://webtoon-phinf.", "://swebtoon-phinf.")
            results.append((url, None))
        return results


class WebtoonsComicExtractor(WebtoonsBase, Extractor):
    """Extractor for an entire comic on webtoons.com"""
    subcategory = "comic"
    categorytransfer = True
    pattern = LANG_PATTERN + r"/([^/?#]+)/([^/?#]+))/list\?([^#]+)"
    example = "https://www.webtoons.com/en/GENRE/TITLE/list?title_no=123"

    def _init(self):
        self.setup_agegate_cookies()

        self.path, self.lang, self.genre, self.comic, query = self.groups
        params = text.parse_query(query)
        self.title_no = params.get("title_no")
        self.page_no = text.parse_int(params.get("page"), 1)

    def items(self):
        page = None
        data = {
            "_extractor": WebtoonsEpisodeExtractor,
            "title_no"  : text.parse_int(self.title_no),
        }

        while True:
            path = "/{}/list?title_no={}&page={}".format(
                self.path, self.title_no, self.page_no)

            if page is not None and path not in page:
                return

            response = self.request(self.root + path)
            if response.history:
                parts = response.url.split("/")
                self.path = "/".join(parts[3:-1])

            page = response.text
            data["page"] = self.page_no

            for url in self.get_episode_urls(page):
                params = text.parse_query(url.rpartition("?")[2])
                data["episode_no"] = text.parse_int(params.get("episode_no"))
                yield Message.Queue, url, data

            self.page_no += 1

    def get_episode_urls(self, page):
        """Extract and return all episode urls in 'page'"""
        page = text.extr(page, 'id="_listUl"', '</ul>')
        return [
            match.group(0)
            for match in WebtoonsEpisodeExtractor.pattern.finditer(page)
        ]


class WebtoonsArtistExtractor(WebtoonsBase, Extractor):
    """Extractor for webtoons.com artists"""
    subcategory = "artist"
    pattern = BASE_PATTERN + r"/p/community/([^/?#]+)/u/([^/?#]+)"
    example = "https://www.webtoons.com/p/community/LANG/u/ARTIST"

    def items(self):
        self.setup_agegate_cookies()

        for comic in self.comics():
            comic["_extractor"] = WebtoonsComicExtractor
            comic_url = self.root + comic["extra"]["episodeListPath"]
            yield Message.Queue, comic_url, comic

    def comics(self):
        lang, artist = self.groups
        language = util.code_to_language(lang).upper()

        url = "{}/p/community/{}/u/{}".format(
            self.root, lang, artist)
        page = self.request(url).text
        creator_id = text.extr(page, '\\"creatorId\\":\\"', '\\')

        url = "{}/p/community/api/v1/creator/{}/titles".format(
            self.root, creator_id)
        params = {
            "language": language,
            "nextSize": "50",
        }
        headers = {
            "language": language,
        }
        data = self.request(url, params=params, headers=headers).json()

        return data["result"]["titles"]
