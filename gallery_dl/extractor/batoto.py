# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bato.to/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, util
from ..cache import memcache

BASE_PATTERN = (r"(?:https?://)?("
                r"(?:ba|d|f|h|j|m|w)to\.to|"
                r"(?:(?:manga|read)toto|batocomic|[xz]bato)\.(?:com|net|org)|"
                r"comiko\.(?:net|org)|"
                r"bat(?:otoo|o?two)\.com)")

#  https://rentry.co/batoto
DOMAINS = {
    "dto.to",
    "fto.to",
    "hto.to",
    "jto.to",
    "mto.to",
    "wto.to",
    "xbato.com",
    "xbato.net",
    "xbato.org",
    "zbato.com",
    "zbato.net",
    "zbato.org",
    "readtoto.com",
    "readtoto.net",
    "readtoto.org",
    "batocomic.com",
    "batocomic.net",
    "batocomic.org",
    "batotoo.com",
    "batotwo.com",
    "comiko.net",
    "comiko.org",
    "battwo.com",
}
LEGACY_DOMAINS = {
    "bato.to",
    "mangatoto.com",
    "mangatoto.net",
    "mangatoto.org",
}


class BatotoBase():
    """Base class for batoto extractors"""
    category = "batoto"
    root = "https://xbato.org"
    _warn_legacy = True

    def _init_root(self):
        domain = self.config("domain")
        if domain is None or domain in {"auto", "url"}:
            domain = self.groups[0]
            if domain in LEGACY_DOMAINS:
                if self._warn_legacy:
                    BatotoBase._warn_legacy = False
                    self.log.warning("Legacy domain '%s'", domain)
        elif domain == "nolegacy":
            domain = self.groups[0]
            if domain in LEGACY_DOMAINS:
                domain = "xbato.org"
        elif domain == "nowarn":
            domain = self.groups[0]
        self.root = "https://" + domain

    def request(self, url, **kwargs):
        kwargs["encoding"] = "utf-8"
        return Extractor.request(self, url, **kwargs)


class BatotoChapterExtractor(BatotoBase, ChapterExtractor):
    """Extractor for batoto manga chapters"""
    archive_fmt = "{chapter_id}_{page}"
    pattern = rf"{BASE_PATTERN}/(?:title/[^/?#]+|chapter)/(\d+)"
    example = "https://xbato.org/title/12345-MANGA/54321"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match, False)
        self._init_root()
        self.chapter_id = self.groups[1]
        self.page_url = f"{self.root}/title/0/{self.chapter_id}"

    def metadata(self, page):
        extr = text.extract_from(page)
        try:
            manga, info, _ = extr("<title>", "<").rsplit(" - ", 3)
        except ValueError:
            manga = info = None

        manga_id = text.extr(
            extr('rel="canonical" href="', '"'), "/title/", "/")

        if not manga:
            manga = extr('link-hover">', "<")
            info = text.remove_html(extr('link-hover">', "</"))
        info = text.unescape(info)

        match = text.re(
            r"(?i)(?:(?:Volume|S(?:eason)?)\s*(\d+)\s+)?"
            r"(?:Chapter|Episode)\s*(\d+)([\w.]*)").match(info)
        if match:
            volume, chapter, minor = match.groups()
        else:
            volume = chapter = 0
            minor = ""

        return {
            **_manga_info(self, manga_id),
            "chapter_url"   : extr(self.chapter_id + "-ch_", '"'),
            "title"         : text.unescape(text.remove_html(extr(
                "selected>", "</option")).partition(" : ")[2]),
            "volume"        : text.parse_int(volume),
            "chapter"       : text.parse_int(chapter),
            "chapter_minor" : minor,
            "chapter_string": info,
            "chapter_id"    : text.parse_int(self.chapter_id),
            "date"          : self.parse_timestamp(extr(' time="', '"')[:-3]),
        }

    def images(self, page):
        images_container = text.extr(page, 'pageOpts', ':[0,0]}"')
        images_container = text.unescape(images_container)
        return [
            (url, None)
            for url in text.extract_iter(images_container, r"\"", r"\"")
        ]


class BatotoMangaExtractor(BatotoBase, MangaExtractor):
    """Extractor for batoto manga"""
    reverse = False
    chapterclass = BatotoChapterExtractor
    pattern = (rf"{BASE_PATTERN}"
               rf"/(?:title/(\d+)[^/?#]*|series/(\d+)(?:/[^/?#]*)?)/?$")
    example = "https://xbato.org/title/12345-MANGA/"

    def __init__(self, match):
        MangaExtractor.__init__(self, match, False)
        self._init_root()
        self.manga_id = self.groups[1] or self.groups[2]
        self.page_url = f"{self.root}/title/{self.manga_id}"

    def chapters(self, page):
        extr = text.extract_from(page)
        if warning := extr(' class="alert alert-warning">', "</div>"):
            self.log.warning("'%s'", text.remove_html(warning))
        extr('<div data-hk="0-0-0-0"', "")
        data = _manga_info(self, self.manga_id, page)

        results = []
        while True:
            href = extr('<a href="/title/', '"')
            if not href:
                break

            chapter = href.rpartition("-ch_")[2]
            chapter, sep, minor = chapter.partition(".")

            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            data["date"] = self.parse_datetime_iso(extr('time="', '"'))

            url = f"{self.root}/title/{href}"
            results.append((url, data.copy()))
        return results


@memcache(keyarg=1)
def _manga_info(self, manga_id, page=None):
    if page is None:
        url = f"{self.root}/title/{manga_id}"
        page = self.request(url).text

    props = text.extract(page, 'props="', '"', page.find(' prefix="r20" '))[0]
    data = util.json_loads(text.unescape(props))["data"][1]

    return {
        "manga"      : data["name"][1],
        "manga_id"   : text.parse_int(manga_id),
        "manga_slug" : data["slug"][1],
        "manga_date" : self.parse_timestamp(
            data["dateCreate"][1] // 1000),
        "manga_date_updated": self.parse_timestamp(
            data["dateUpdate"][1] / 1000),
        "author"     : json_list(data["authors"]),
        "artist"     : json_list(data["artists"]),
        "genre"      : json_list(data["genres"]),
        "lang"       : data["tranLang"][1],
        "lang_orig"  : data["origLang"][1],
        "status"     : data["originalStatus"][1],
        "published"  : data["originalPubFrom"][1],
        "description": data["summary"][1]["code"][1],
        "cover"      : data["urlCoverOri"][1],
        "uploader"   : data["userId"][1],
        "score"      : data["stat_score_avg"][1],
    }


def json_list(value):
    return [
        item[1].replace("_", " ")
        for item in util.json_loads(value[1].replace('\\"', '"'))
    ]
