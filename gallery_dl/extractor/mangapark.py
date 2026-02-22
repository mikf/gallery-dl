# -*- coding: utf-8 -*-

# Copyright 2015-2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://mangapark.net/"""

from .common import ChapterExtractor, Extractor, Message
from .. import text, util

BASE_PATTERN = (r"(?:https?://)?(?:www\.)?(?:"
                r"(?:manga|comic|read)park\.(?:com|net|org|me|io|to)|"
                r"parkmanga\.(?:com|net|org)|"
                r"mpark\.to)")


class MangaparkBase():
    """Base class for mangapark extractors"""
    category = "mangapark"

    def _parse_chapter_title(self, title):
        match = text.re(
            r"(?i)"
            r"(?:vol(?:\.|ume)?\s*(\d+)\s*)?"
            r"ch(?:\.|apter)?\s*(\d+)([^\s:]*)"
            r"(?:\s*:\s*(.*))?"
        ).match(title)
        return match.groups() if match else (0, 0, "", "")

    def _extract_manga(self, manga_id):
        variables = {
            "getComicNodeId": manga_id,
        }
        return self._request_graphql("Get_comicNode", variables)["data"]

    def _extract_chapter(self, chapter_id):
        variables = {
            "getChapterNodeId": chapter_id,
        }
        return self._request_graphql("Get_chapterNode", variables)["data"]

    def _extract_chapters_all(self, manga_id):
        variables = {
            "comicId": manga_id,
        }
        return self._request_graphql("Get_comicChapterList", variables)

    def _extract_chapters_source(self, source_id):
        variables = {
            "sourceId": source_id,
        }
        return self._request_graphql(
            "get_content_source_chapterList", variables)

    def _request_graphql(self, opname, variables):
        url = self.root + "/apo/"
        data = {
            "query"        : self.utils("graphql", opname),
            "variables"    : variables,
            "operationName": opname,
        }
        return self.request_json(
            url, method="POST", json=data)["data"].popitem()[1]


class MangaparkChapterExtractor(MangaparkBase, ChapterExtractor):
    """Extractor for manga-chapters from mangapark.net"""
    pattern = (BASE_PATTERN +
               r"/(?:title/[^/?#]+/|comic/\d+/[^/?#]+/[^/?#]+-i)(\d+)")
    example = "https://mangapark.net/title/MANGA/12345-en-ch.01"

    def __init__(self, match):
        self.root = text.root_from_url(match[0])
        ChapterExtractor.__init__(self, match, False)

    def metadata(self, _):
        chapter = self._extract_chapter(self.groups[0])
        manga = self.cache(self._extract_manga, chapter["comicNode"]["id"])

        self._urls = chapter["imageFile"]["urlList"]
        vol, ch, minor, title = self._parse_chapter_title(chapter["dname"])
        lang = chapter.get("lang") or "en"

        return {
            "manga"     : manga["name"],
            "manga_id"  : text.parse_int(manga["id"]),
            "artist"    : manga["artists"],
            "author"    : manga["authors"],
            "genre"     : manga["genres"],
            "volume"    : text.parse_int(vol),
            "chapter"   : text.parse_int(ch),
            "chapter_minor": minor,
            "chapter_id": text.parse_int(chapter["id"]),
            "title"     : title or "",
            "lang"      : lang,
            "language"  : util.code_to_language(lang),
            "source"    : chapter["srcTitle"],
            "source_id" : chapter["sourceId"],
            "date"      : self.parse_timestamp(chapter["dateCreate"] / 1000),
        }

    def images(self, _):
        return [(url, None) for url in self._urls]


class MangaparkMangaExtractor(MangaparkBase, Extractor):
    """Extractor for manga from mangapark.net"""
    subcategory = "manga"
    pattern = BASE_PATTERN + r"/(?:title|comic)/(\d+)(?:[/-][^/?#]*)?/?$"
    example = "https://mangapark.net/title/12345-MANGA"

    def __init__(self, match):
        self.root = text.root_from_url(match[0])
        self.manga_id = int(match[1])
        Extractor.__init__(self, match)

    def items(self):
        for chapter in self.chapters():
            chapter = chapter["data"]
            url = self.root + chapter["urlPath"]

            vol, ch, minor, title = self._parse_chapter_title(chapter["dname"])
            lang = chapter.get("lang") or "en"

            data = {
                "manga_id"  : self.manga_id,
                "volume"    : text.parse_int(vol),
                "chapter"   : text.parse_int(ch),
                "chapter_minor": minor,
                "chapter_id": chapter["id"],
                "title"     : chapter["title"] or title or "",
                "lang"      : lang,
                "language"  : util.code_to_language(lang),
                "source"    : chapter["srcTitle"],
                "source_id" : chapter["sourceId"],
                "date"      : self.parse_timestamp(
                    chapter["dateCreate"] / 1000),
                "_extractor": MangaparkChapterExtractor,
            }
            yield Message.Queue, url, data

    def chapters(self):
        if source := self.config("source"):
            source_id = self._select_source(source)
            self.log.debug("Requesting chapters for source_id %s", source_id)
            chapters = self._extract_chapters_source(source_id)
        else:
            chapters = self._extract_chapters_all(self.groups[0])

        if self.config("chapter-reverse"):
            chapters.reverse()
        return chapters

    def _select_source(self, source):
        if isinstance(source, int):
            return source

        group, _, lang = source.partition(":")
        group = group.lower()

        variables = {
            "comicId"    : self.manga_id,
            "dbStatuss"  : ["normal"],
            "haveChapter": True,
        }
        for item in self._request_graphql(
                "get_content_comic_sources", variables):
            data = item["data"]
            if (not group or data["srcTitle"].lower() == group) and (
                    not lang or data["lang"] == lang):
                return data["id"]

        raise self.exc.AbortExtraction(
            f"'{source}' does not match any available source")
