# -*- coding: utf-8 -*-

# Copyright 2020 Leonardo Taccari
# Copyright 2021-2025 Mike Fährmann
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
    directory_fmt = ("{category}", "{comic}")
    filename_fmt = "{episode_no}-{num:>02}{type:?-//}.{extension}"
    archive_fmt = "{title_no}_{episode_no}_{num}"
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

    _init = setup_agegate_cookies

    def request(self, url, **kwargs):
        response = Extractor.request(self, url, **kwargs)
        if response.history and "/ageGate" in response.url:
            raise exception.AbortExtraction(
                f"HTTP redirect to age gate check ('{response.url}')")
        return response


class WebtoonsEpisodeExtractor(WebtoonsBase, GalleryExtractor):
    """Extractor for an episode on webtoons.com"""
    subcategory = "episode"
    pattern = (rf"{LANG_PATTERN}/([^/?#]+)/([^/?#]+)/[^/?#]+)"
               r"/viewer\?([^#'\"]+)")
    example = ("https://www.webtoons.com/en/GENRE/TITLE/NAME/viewer"
               "?title_no=123&episode_no=12345")

    def _init(self):
        self.setup_agegate_cookies()

        base, self.lang, self.genre, self.comic, query = self.groups
        params = text.parse_query(query)
        self.title_no = params.get("title_no")
        self.episode_no = params.get("episode_no")
        self.page_url = f"{self.root}/{base}/viewer?{query}"

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr('<meta property="og:title" content="', '"')
        descr = extr('<meta property="og:description" content="', '"')

        if extr('<div class="subj_info"', '\n'):
            comic_name = extr(">", "<")
            episode_name = extr('<h1 class="subj_episode" title="', '"')
        else:
            comic_name = episode_name = ""

        if extr('<span class="tx _btnOpenEpisodeLis', '"'):
            episode = extr(">#", "<")
        else:
            episode = ""

        if extr('<span class="author"', "\n"):
            username = extr("/u/", '"')
            author_name = extr("<span>", "</span>")
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
                    url = f"{path}?type={type}"

            results.append((_url(url), None))
        return results

    def assets(self, page):
        if self.config("thumbnails", False):
            active = text.extr(page, 'class="on', '</a>')
            url = _url(text.extr(active, 'data-url="', '"'))
            return ({"url": url, "type": "thumbnail"},)


class WebtoonsComicExtractor(WebtoonsBase, Extractor):
    """Extractor for an entire comic on webtoons.com"""
    subcategory = "comic"
    categorytransfer = True
    filename_fmt = "{type}.{extension}"
    archive_fmt = "{title_no}_{type}"
    pattern = rf"{LANG_PATTERN}/([^/?#]+)/([^/?#]+))/list\?([^#]+)"
    example = "https://www.webtoons.com/en/GENRE/TITLE/list?title_no=123"

    def items(self):
        kw = self.kwdict
        base, kw["lang"], kw["genre"], kw["comic"], query = self.groups
        params = text.parse_query(query)
        kw["title_no"] = title_no = text.parse_int(params.get("title_no"))
        kw["page"] = page_no = text.parse_int(params.get("page"), 1)

        path = f"/{base}/list?title_no={title_no}&page={page_no}"
        response = self.request(self.root + path)
        if response.history:
            parts = response.url.split("/")
            base = "/".join(parts[3:-1])
        page = response.text

        if self.config("banners") and (asset := self._asset_banner(page)):
            yield Message.Directory, "", asset
            yield Message.Url, asset["url"], asset

        data = {"_extractor": WebtoonsEpisodeExtractor}
        while True:
            for url in self.get_episode_urls(page):
                params = text.parse_query(url.rpartition("?")[2])
                data["episode_no"] = text.parse_int(params.get("episode_no"))
                yield Message.Queue, url, data

            kw["page"] = page_no = page_no + 1
            path = f"/{base}/list?title_no={title_no}&page={page_no}"
            if path not in page:
                return
            page = self.request(self.root + path).text

    def get_episode_urls(self, page):
        """Extract and return all episode urls in 'page'"""
        page = text.extr(page, 'id="_listUl"', "</ul>")
        return [
            match[0]
            for match in WebtoonsEpisodeExtractor.pattern.finditer(page)
        ]

    def _asset_banner(self, page):
        try:
            pos = page.index('<span class="thmb')
        except Exception:
            return

        url = _url(text.extract(page, 'src="', '"', pos)[0])
        return text.nameext_from_url(url, {"url": url, "type": "banner"})


class WebtoonsArtistExtractor(WebtoonsBase, Extractor):
    """Extractor for webtoons.com artists"""
    subcategory = "artist"
    pattern = rf"{BASE_PATTERN}/p/community/([^/?#]+)/u/([^/?#]+)"
    example = "https://www.webtoons.com/p/community/LANG/u/ARTIST"

    def items(self):
        for comic in self.comics():
            comic["_extractor"] = WebtoonsComicExtractor
            comic_url = self.root + comic["extra"]["episodeListPath"]
            yield Message.Queue, comic_url, comic

    def comics(self):
        lang, artist = self.groups
        language = util.code_to_language(lang).upper()

        url = f"{self.root}/p/community/{lang}/u/{artist}"
        page = self.request(url).text
        creator_id = text.extr(page, '\\"creatorId\\":\\"', '\\')

        url = f"{self.root}/p/community/api/v1/creator/{creator_id}/titles"
        params = {
            "language": language,
            "nextSize": "50",
        }
        headers = {
            "language": language,
        }
        data = self.request_json(url, params=params, headers=headers)

        return data["result"]["titles"]


def _url(url):
    return url.replace("://webtoon-phinf.", "://swebtoon-phinf.")
