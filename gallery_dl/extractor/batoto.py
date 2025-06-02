# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bato.to/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import re

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
    pattern = BASE_PATTERN + r"/(?:title/[^/?#]+|chapter)/(\d+)"
    example = "https://xbato.org/title/12345-MANGA/54321"

    def __init__(self, match):
        ChapterExtractor.__init__(self, match, False)
        self._init_root()
        self.chapter_id = self.groups[1]
        self.gallery_url = "{}/title/0/{}".format(self.root, self.chapter_id)

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

        match = re.match(
            r"(?i)(?:(?:Volume|S(?:eason)?)\s*(\d+)\s+)?"
            r"(?:Chapter|Episode)\s*(\d+)([\w.]*)", info)
        if match:
            volume, chapter, minor = match.groups()
        else:
            volume = chapter = 0
            minor = ""

        return {
            "manga"         : text.unescape(manga),
            "manga_id"      : text.parse_int(manga_id),
            "chapter_url"   : extr(self.chapter_id + "-ch_", '"'),
            "title"         : text.unescape(text.remove_html(extr(
                "selected>", "</option")).partition(" : ")[2]),
            "volume"        : text.parse_int(volume),
            "chapter"       : text.parse_int(chapter),
            "chapter_minor" : minor,
            "chapter_string": info,
            "chapter_id"    : text.parse_int(self.chapter_id),
            "date"          : text.parse_timestamp(extr(' time="', '"')[:-3]),
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
    pattern = (BASE_PATTERN +
               r"/(?:title/(\d+)[^/?#]*|series/(\d+)(?:/[^/?#]*)?)/?$")
    example = "https://xbato.org/title/12345-MANGA/"

    def __init__(self, match):
        MangaExtractor.__init__(self, match, False)
        self._init_root()
        self.manga_id = self.groups[1] or self.groups[2]
        self.manga_url = "{}/title/{}".format(self.root, self.manga_id)

    def chapters(self, page):
        extr = text.extract_from(page)

        warning = extr(' class="alert alert-warning">', "</div><")
        if warning:
            raise exception.StopExtraction("'%s'", text.remove_html(warning))

        data = {
            "manga_id": text.parse_int(self.manga_id),
            "manga"   : text.unescape(extr(
                "<title>", "<").rpartition(" - ")[0]),
        }

        extr('<div data-hk="0-0-0-0"', "")
        results = []
        while True:
            href = extr('<a href="/title/', '"')
            if not href:
                break

            chapter = href.rpartition("-ch_")[2]
            chapter, sep, minor = chapter.partition(".")

            data["chapter"] = text.parse_int(chapter)
            data["chapter_minor"] = sep + minor
            data["date"] = text.parse_datetime(
                extr('time="', '"'), "%Y-%m-%dT%H:%M:%S.%fZ")

            url = "{}/title/{}".format(self.root, href)
            results.append((url, data.copy()))
        return results
