# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangaread.org/"""

from .common import ChapterExtractor, MangaExtractor
from .. import text, exception
import re


class MangareadBase():
    """Base class for Mangaread extractors"""
    category = "mangaread"
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


class MangareadChapterExtractor(MangareadBase, ChapterExtractor):
    """Extractor for manga-chapters from mangaread.org"""
    pattern = (r"(?:https?://)?(?:www\.)?mangaread\.org"
               r"(/manga/[^/?#]+/[^/?#]+)")
    example = "https://www.mangaread.org/manga/MANGA/chapter-01/"

    def metadata(self, page):
        tags = text.extr(page, 'class="wp-manga-tags-list">', '</div>')
        data = {"tags": list(text.split_html(tags)[::2])}
        info = text.extr(page, '<h1 id="chapter-heading">', "</h1>")
        if not info:
            raise exception.NotFoundError("chapter")
        self.parse_chapter_string(info, data)
        return data

    def images(self, page):
        page = text.extr(
            page, '<div class="reading-content">', '<div class="entry-header')
        return [
            (text.extr(img, 'src="', '"').strip(), None)
            for img in text.extract_iter(page, '<img id="image-', '>')
        ]


class MangareadMangaExtractor(MangareadBase, MangaExtractor):
    """Extractor for manga from mangaread.org"""
    chapterclass = MangareadChapterExtractor
    pattern = r"(?:https?://)?(?:www\.)?mangaread\.org(/manga/[^/?#]+)/?$"
    example = "https://www.mangaread.org/manga/MANGA"

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
        return {
            "manga"      : text.extr(page, "<h1>", "</h1>").strip(),
            "description": text.unescape(text.remove_html(text.extract(
                page, ">", "</div>", page.index("summary__content"))[0])),
            "rating"     : text.parse_float(
                extr('total_votes">', "</span>").strip()),
            "manga_alt"  : text.remove_html(
                extr("Alternative </h5>\n</div>", "</div>")).split("; "),
            "author"     : list(text.extract_iter(
                extr('class="author-content">', "</div>"), '"tag">', "</a>")),
            "artist"     : list(text.extract_iter(
                extr('class="artist-content">', "</div>"), '"tag">', "</a>")),
            "genres"     : list(text.extract_iter(
                extr('class="genres-content">', "</div>"), '"tag">', "</a>")),
            "type"       : text.remove_html(
                extr("	Type	", "\n</div>")),
            "release"    : text.parse_int(text.remove_html(
                extr("	Release	", "\n</div>"))),
            "status"     : text.remove_html(
                extr("	Status	", "\n</div>")),
        }
