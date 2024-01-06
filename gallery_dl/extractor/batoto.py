# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://bato.to/"""

from .common import Extractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import re

BASE_PATTERN = (r"(?:https?://)?"
                r"(?:(?:ba|d|w)to\.to|\.to|(?:batotoo|mangatoto)\.com)")


class BatotoBase():
    """Base class for batoto extractors"""
    category = "batoto"
    root = "https://bato.to"

    def request(self, url, **kwargs):
        kwargs["encoding"] = "utf-8"
        return Extractor.request(self, url, **kwargs)


class BatotoChapterExtractor(BatotoBase, ChapterExtractor):
    """Extractor for bato.to manga chapters"""
    pattern = BASE_PATTERN + r"/(?:title/[^/?#]+|chapter)/(\d+)"
    example = "https://bato.to/title/12345-MANGA/54321"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.chapter_id = match.group(1)
        url = "{}/title/0/{}".format(self.root, self.chapter_id)
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        extr = text.extract_from(page)
        manga, info, _ = extr("<title>", "<").rsplit(" - ", 3)
        manga_id = extr("/title/", "/")

        match = re.match(
            r"(?:Volume\s+(\d+) )?"
            r"\w+\s+(\d+)(.*)", info)
        if match:
            volume, chapter, minor = match.groups()
            title = text.remove_html(extr(
                "selected>", "</option")).partition(" : ")[2]
        else:
            volume = chapter = 0
            minor = ""
            title = info

        return {
            "manga"        : text.unescape(manga),
            "manga_id"     : text.parse_int(manga_id),
            "title"        : text.unescape(title),
            "volume"       : text.parse_int(volume),
            "chapter"      : text.parse_int(chapter),
            "chapter_minor": minor,
            "chapter_id"   : text.parse_int(self.chapter_id),
            "date"         : text.parse_timestamp(extr(' time="', '"')[:-3]),
        }

    def images(self, page):
        images_container = text.extr(page, 'pageOpts', ':[0,0]}"')
        images_container = text.unescape(images_container)
        return [
            (url, None)
            for url in text.extract_iter(images_container, r"\"", r"\"")
        ]


class BatotoMangaExtractor(BatotoBase, MangaExtractor):
    """Extractor for bato.to manga"""
    reverse = False
    chapterclass = BatotoChapterExtractor
    pattern = BASE_PATTERN + r"/(?:title|series)/(\d+)[^/?#]*/?$"
    example = "https://bato.to/title/12345-MANGA/"

    def __init__(self, match):
        self.root = text.root_from_url(match.group(0))
        self.manga_id = match.group(1)
        url = "{}/title/{}".format(self.root, self.manga_id)
        MangaExtractor.__init__(self, match, url)

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
