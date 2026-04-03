# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://allporncomic.com/"""

from .common import Extractor, ChapterExtractor, MangaExtractor, Message
from .. import text

BASE_PATTERN = r"(?:https?://)?(?:www\.)?allporncomic\.com"


class AllporncomicBase():
    """Base class for allporncomic extractors"""
    category = "allporncomic"
    root = "https://allporncomic.com"

    def _manga_info(self, slug, page=None):
        if page is None:
            url = f"{self.root}/porncomic/{slug}/"
            page = self.request(url).text
        extr = text.extract_from(page)

        lang = extr('property="og:locale" content="', '"')
        title = text.unescape(extr('property="og:title" content="', '"'))
        manga = text.re(r"(.+?)( \([^)]+\))?( \[[^\]]+\])?\s*$").match(title)

        return {
            "description" : text.unescape(extr(
                'property="og:description" content="', '"')),
            "manga"       : "" if manga is None else manga[1],
            "manga_slug"  : slug,
            "manga_cover" : extr('property="og:image" content="', '"'),
            "manga_date"  : self.parse_datetime_iso(extr(
                '"datePublished":"', '"')),
            "manga_date_updated": self.parse_datetime_iso(extr(
                '"dateModified":"', '"')),
            "manga_id"    : text.parse_int(extr(" postid-", " ")),
            "rating"      : text.parse_float(extr('total_votes">', "<")),
            "votes"       : text.parse_int(extr('id="countrate">', "<")),
            "characters"  : text.split_html(extr(
                'class="author-content">', "</div>"))[::2],
            "parody"      : text.split_html(extr(
                'class="author-content">', "</div>"))[::2],
            "group"       : text.split_html(extr(
                'class="author-content">', "</div>"))[::2],
            "artist"      : text.split_html(extr(
                'class="artist-content">', "</div>"))[::2],
            "tags"        : text.split_html(extr(
                'class="genres-content">', "</div>"))[::2],
            "type"        : extr('class="summary-content">', "<").strip(),
            "status"      : extr('class="summary-content">', "<").strip(),
            "comments"    : text.parse_int(extr('<span>', " ")),
            "bookmarks"   : text.parse_int(extr(
                'class="action_detail"><span>', " ")),
            "lang"        : lang.partition("_")[0],
        }


class AllporncomicChapterExtractor(AllporncomicBase, ChapterExtractor):
    """Extractor for allporncomic manga chapters"""
    directory_fmt = ("{category}", "{path[:-1]:I}", "{title}")
    filename_fmt = "{page:>03}.{extension}"
    archive_fmt = "{manga_id}_{chapter_id}_{page}"
    pattern = (BASE_PATTERN +
               r"(/porncomic/([^/?#]+)/(\d+(?:-\d+)?)?([^/?#]+))")
    example = "https://allporncomic.com/porncomic/MANGA/123-TITLE/"

    def __init__(self, match):
        url = f"{self.root}{match[1]}/"
        ChapterExtractor.__init__(self, match, url)

    def metadata(self, page):
        _, manga_slug, chapter, title_slug = self.groups
        if chapter is None:
            chapter = sep = minor = ""
        else:
            chapter, sep, minor = chapter.partition("-")

        if '<source src="' in page:
            media = "video"
            self.needle = '<source src="'
        else:
            media = "image"
            self.needle = ' data-src="'

        path = text.split_html(text.extr(
            page, '<ol class="breadcrumb', '</ol>'))
        title = text.re(
            r"^(?:\s*\d+(?:\.\d+)?\s*\.|\[[^\]]+\])\s").sub("", path[-1])
        title = text.re(
            r"(?:\s+-)?"
            r"(?:\s+[Cc]hapter \d+(?:\s+[Ee]xtras)?)?"
            r"(?:\s+\([^)]+\))?"
            r"(?:\s+(?:-\s+)?\[[^\]]+\])?\s*$").sub("", title)

        return {
            **self.cache(self._manga_info, manga_slug),
            "path"         : path[3:],
            "media"        : media,
            "title"        : title,
            "title_slug"   : title_slug.lstrip("-"),
            "chapter"      : text.parse_int(chapter),
            "chapter_id"   : text.parse_int(text.extr(
                page, 'manga_chapter_id" value="', '"')),
            "chapter_minor": "." + minor if minor else "",
        }

    def images(self, page):
        return [
            (url.strip(), None)
            for url in text.extract_iter(page, self.needle, '"')
        ]


class AllporncomicMangaExtractor(AllporncomicBase, MangaExtractor):
    """Extractor for allporncomic manga"""
    chapterclass = AllporncomicChapterExtractor
    pattern = BASE_PATTERN + r"/porncomic/([^/?#]+)"
    example = "https://allporncomic.com/porncomic/MANGA/"

    def __init__(self, match):
        url = f"{self.root}/porncomic/{match[1]}/"
        MangaExtractor.__init__(self, match, url)

    def chapters(self, page):
        slug = text.extr(page, "/porncomic/", "/")
        info = self._manga_info(slug, page)

        results = []
        for ch in text.extract_iter(
                page, '<li class="wp-manga-chapter', '</li>'):
            url = text.extr(ch, ' href="', '"')
            data = {
                **info,
                "date": self.parse_datetime(text.extr(
                    page, "<i>", "<"), "%B %d, %Y"),
            }
            results.append((url, data))
        return results


class AllporncomicTagExtractor(AllporncomicBase, Extractor):
    """Extractor for allporncomic tag search results"""
    subcategory = "tag"
    pattern = (BASE_PATTERN + r"(/(?:porncomic-)?"
               r"(?:genre|series|group|artist|characters)"
               r"/[^/?#]+(?:/page/\d+)?)(/?\?[^#]+)?")
    example = "https://allporncomic.com/porncomic-genre/GENRE/"

    def items(self):
        data = {"_extractor": AllporncomicMangaExtractor}

        url = f"{self.root}{self.groups[0]}{self.groups[1] or '/'}"
        while url:
            page = self.request(url).text

            for manga in text.extract_iter(page, 'id="manga-item-', "</div>"):
                yield Message.Queue, text.extr(manga, ' href="', '"'), data

            url = text.extr(page, '<link rel="next" href="', '"')
