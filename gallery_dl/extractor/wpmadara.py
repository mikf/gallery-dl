# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for WordPressMadara based websites."""

from .common import BaseExtractor, ChapterExtractor, MangaExtractor
from .. import text, exception
import re


class WPMadaraBase(BaseExtractor):
    """Base class for WordPressMadara based extractors"""
    basecategory = "wpmadara"
    root = "https://www.mangaread.org"

    @staticmethod
    def parse_chapter_string(chapter_string, data):
        match = re.match(
            r"(?:(.+)\s*-\s*)?[Cc]hapter\s*(\d+)(\.\d+)?(?:\s*-\s*(.+))?",
            text.unescape(chapter_string).strip())
        manga, chapter, minor, title = match.groups()
        manga = manga.strip() if manga else ""
        data["manga"] = data.pop("manga", manga)
        data["chapter"] = text.parse_int(chapter)
        data["chapter_minor"] = minor or ""
        data["title"] = title or ""
        data["lang"] = "en"
        data["language"] = "English"


BASE_PATTERN = WPMadaraBase.update({
    "mangaread": {
        "root": "https://www.mangaread.org",
        "pattern": r"(?:https?://)?(?:www\.)?mangaread\.org",
    },
    "toonily": {
        "root": "https://www.toonily.com",
        "pattern": r"(?:https?://)?(?:www\.)?toonily\.com",
    },
    "webtoonxyz": {
        "root": "https://www.webtoon.xyz",
        "pattern": r"(?:https?://)?(?:www\.)?webtoon\.xyz",
    },
})


class WPMadaraChapterExtractor(WPMadaraBase, ChapterExtractor):
    """Extractor for manga-chapters from WordPressMadara based websites."""
    subcategory = "chapter"
    pattern = BASE_PATTERN + r"(/(manga|webtoon|read)/[^/?#]+/[^/?#]+)"
    example = "https://www.mangaread.org/manga/MANGA/chapter-01/"

    def __init__(self, match, url=None):
        WPMadaraBase.__init__(self, match)
        self.chapter = match.group(match.lastindex)
        self.log.debug("chapter: %s", self.chapter)
        self.gallery_url = self.root + match.group(match.lastindex)

        if self.config("chapter-reverse", False):
            self.reverse = not self.reverse

    def metadata(self, page):
        tags = text.extr(page, 'class="wp-manga-tags-list">', '</div>')
        data = {"tags": list(text.split_html(tags)[::2])}
        info = text.extr(page, '<h1 id="chapter-heading">', "</h1>")
        if not info:
            raise exception.NotFoundError("chapter")
        self.parse_chapter_string(info, data)
        self.log.debug("data: %s", data)
        return data

    def images(self, page):
        page = text.extr(
            page, '<div class="reading-content">', '<div class="entry-header')
        self.log.debug("page: %s", page)
        return [
            (text.extr(img, 'src="', '"').strip(), None)
            for img in text.extract_iter(page, '<img id="image-', '>')
        ]


class WPMadaraMangaExtractor(WPMadaraBase, MangaExtractor):
    """Extractor for manga from WordPressMadara based websites."""
    chapterclass = WPMadaraChapterExtractor
    subcategory = "manga"
    pattern = BASE_PATTERN + r"(/(manga|webtoon|read)/[^/?#]+)/?$"
    example = "https://www.mangaread.org/manga/MANGA"

    def __init__(self, match, url=None):
        WPMadaraBase.__init__(self, match)
        self.manga = match.group(match.lastindex)
        self.manga_url = url or self.root + match.group(match.lastindex)

    def chapters(self, page):
        if 'class="error404' in page:
            raise exception.NotFoundError("manga")
        data = self.metadata(page)
        result = []
        for chapter in text.extract_iter(
                page, '<li class="wp-manga-chapter', "</li>"):
            url , pos = text.extract(chapter, '<a href="', '"')
            info, _ = text.extract(chapter, ">", "</a>", pos)
            self.parse_chapter_string(info, data)
            result.append((url, data.copy()))
        return result

    def metadata(self, page):
        extr = text.extract_from(text.extr(
            page, 'class="summary_content">', 'class="manga-action"'))
        # rating = 0.0
        if len(text.extr(page, 'total_votes">', "</span>").strip()) > 0:
            rating = text.parse_float(text.extr(
                page, 'total_votes">', "</span>").strip())
        elif len(text.extr(page, 'property="ratingValue" id="averagerate">',
                           "</span>").strip()) > 0:
            rating = text.parse_float(
                text.extr(page,
                          'property="ratingValue" id="averagerate">',
                          "</span>").strip())
        else:
            rating = 0.0

        return {
            "manga"      : text.extr(page, "<h1>", "</h1>").strip(),
            "description": text.unescape(text.remove_html(text.extract(
                page, ">", "</div>", page.index("summary__content"))[0])),
            "rating"     : rating,
            "manga_alt"  : text.remove_html(
                extr("Alternative </h5>\n</div>", "</div>")).split("; "),
            "author"     : list(text.extract_iter(
                extr('class="author-content">', "</div>"), '"tag">', "</a>")),
            "artist"     : list(text.extract_iter(
                extr('class="artist-content">', "</div>"), '"tag">', "</a>")),
            "genres"     : list(text.extract_iter(
                extr('class="genres-content">', "</div>"), '"tag">', "</a>")),
            "type"       : text.remove_html(
                extr("Type </h5>\n</div>", "</div>")),
            "release"    : text.parse_int(text.remove_html(
                extr("Release </h5>\n</div>", "</div>"))),
            "status"     : text.remove_html(
                extr("Status </h5>\n</div>", "</div>")),
        }
